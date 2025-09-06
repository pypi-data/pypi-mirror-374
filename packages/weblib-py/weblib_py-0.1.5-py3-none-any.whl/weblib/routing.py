"""
Sistema di routing per WebLib
"""

from typing import Dict, Callable, Any, Optional, Tuple
import re
from urllib.parse import parse_qs
from .html import HtmlElement


class Route:
    """Rappresenta una singola route"""
    
    def __init__(self, pattern: str, handler: Callable, methods: Optional[list] = None):
        self.pattern = pattern
        self.handler = handler
        self.methods = methods or ['GET', 'HEAD']
        self.regex_pattern = self._compile_pattern(pattern)
    
    def _compile_pattern(self, pattern: str) -> re.Pattern:
        """Converte un pattern di route in regex"""
        # Converte pattern tipo '/user/<id>' in regex
        regex_pattern = pattern
        
        # Sostituisce i parametri con gruppi di cattura
        regex_pattern = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', regex_pattern)
        
        # Aggiungi inizio e fine stringa
        regex_pattern = f'^{regex_pattern}$'
        
        return re.compile(regex_pattern)
    
    def match(self, path: str) -> Optional[Dict[str, str]]:
        """Verifica se il path corrisponde a questa route"""
        match = self.regex_pattern.match(path)
        if match:
            return match.groupdict()
        return None


class Request:
    """Rappresenta una richiesta HTTP"""
    
    def __init__(self, method: str, path: str, query_string: str = "", 
                 headers: Optional[Dict[str, str]] = None, 
                 form_data: Optional[Dict[str, Any]] = None,
                 cookies: Optional[Dict[str, str]] = None):
        self.method = method
        self.path = path
        self.query_string = query_string
        self.headers = headers or {}
        self.form_data = form_data or {}
        self.cookies = cookies or {}
        self.args = self._parse_query_string(query_string)
        self.state = type('State', (), {})  # For storing arbitrary data during request processing
        
    def _parse_query_string(self, query_string: str) -> Dict[str, str]:
        """Analizza la query string e restituisce un dizionario"""
        if not query_string:
            return {}
        
        parsed = parse_qs(query_string)
        # Converte le liste in valori singoli per semplicità
        return {key: values[0] if values else "" for key, values in parsed.items()}


class Response:
    """Rappresenta una risposta HTTP"""
    
    def __init__(self, content: str = "", status_code: int = 200, 
                 headers: Optional[Dict[str, str]] = None, content_type: str = "text/html"):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
        self.headers.setdefault('Content-Type', content_type)
        self.cookies = []
    
    def set_header(self, name: str, value: str) -> 'Response':
        """Imposta un header della risposta"""
        self.headers[name] = value
        return self
    
    def set_status(self, status_code: int) -> 'Response':
        """Imposta lo status code"""
        self.status_code = status_code
        return self
    
    def set_cookie(self, key: str, value: str, max_age: int = None, 
                   expires: int = None, path: str = "/", domain: str = None, 
                   secure: bool = False, httponly: bool = False, 
                   samesite: str = "lax") -> 'Response':
        """Set a cookie in the response"""
        self.cookies.append({
            'key': key,
            'value': value,
            'max_age': max_age,
            'expires': expires,
            'path': path,
            'domain': domain,
            'secure': secure,
            'httponly': httponly,
            'samesite': samesite
        })
        return self
    
    def delete_cookie(self, key: str, path: str = "/", domain: str = None) -> 'Response':
        """Delete a cookie by setting its expiry in the past"""
        return self.set_cookie(key, "", max_age=0, expires=0, path=path, domain=domain)


class Router:
    """Gestore delle route dell'applicazione"""
    
    def __init__(self):
        self.routes: list[Route] = []
        self.error_handlers: Dict[int, Callable] = {}
    
    def add_route(self, pattern: str, handler: Callable, methods: Optional[list] = None) -> None:
        """Aggiunge una nuova route"""
        route = Route(pattern, handler, methods)
        self.routes.append(route)
    
    def route(self, pattern: str, methods: Optional[list] = None):
        """Decorator per aggiungere route"""
        def decorator(handler: Callable):
            self.add_route(pattern, handler, methods)
            return handler
        return decorator
    
    def get(self, pattern: str):
        """Decorator per route GET e HEAD"""
        return self.route(pattern, ['GET', 'HEAD'])
    
    def post(self, pattern: str):
        """Decorator per route POST"""
        return self.route(pattern, ['POST'])
    
    def put(self, pattern: str):
        """Decorator per route PUT"""
        return self.route(pattern, ['PUT'])
    
    def delete(self, pattern: str):
        """Decorator per route DELETE"""
        return self.route(pattern, ['DELETE'])
    
    def error_handler(self, status_code: int):
        """Decorator per gestori di errore"""
        def decorator(handler: Callable):
            self.error_handlers[status_code] = handler
            return handler
        return decorator
    
    def match_route(self, path: str, method: str) -> Optional[Tuple[Route, Dict[str, str]]]:
        """Trova la route corrispondente al path e metodo"""
        for route in self.routes:
            if method in route.methods:
                params = route.match(path)
                if params is not None:
                    return route, params
        return None
    
    def dispatch(self, request: Request) -> Response:
        """Gestisce una richiesta e restituisce una risposta"""
        try:
            match_result = self.match_route(request.path, request.method)
            
            if match_result:
                route, params = match_result
                
                # Chiama il gestore con i parametri
                try:
                    result = route.handler(request, **params)
                    
                    # Se il risultato è già una Response, la restituisce
                    if isinstance(result, Response):
                        return result
                    
                    # Se il risultato è un HtmlElement, lo renderizza
                    elif isinstance(result, HtmlElement):
                        return Response(result.render())
                    
                    # Se è una stringa, la usa come contenuto
                    elif isinstance(result, str):
                        return Response(result)
                    
                    # Se è un dict, lo converte in JSON (per API)
                    elif isinstance(result, dict):
                        import json
                        return Response(
                            json.dumps(result), 
                            content_type="application/json"
                        )
                    
                    else:
                        return Response(str(result))
                        
                except Exception as e:
                    # Gestisce errori del gestore
                    return self._handle_error(500, f"Internal Server Error: {str(e)}")
            else:
                # Route non trovata
                return self._handle_error(404, "Not Found")
                
        except Exception as e:
            # Errore generico
            return self._handle_error(500, f"Internal Server Error: {str(e)}")
    
    def _handle_error(self, status_code: int, message: str) -> Response:
        """Gestisce gli errori utilizzando i gestori personalizzati se disponibili"""
        if status_code in self.error_handlers:
            try:
                result = self.error_handlers[status_code](message)
                if isinstance(result, Response):
                    return result
                elif isinstance(result, HtmlElement):
                    return Response(result.render(), status_code=status_code)
                else:
                    return Response(str(result), status_code=status_code)
            except:
                pass
        
        # Gestore di errore predefinito
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error {status_code}</title>
        </head>
        <body>
            <h1>Error {status_code}</h1>
            <p>{message}</p>
        </body>
        </html>
        """
        
        return Response(error_html, status_code=status_code)
