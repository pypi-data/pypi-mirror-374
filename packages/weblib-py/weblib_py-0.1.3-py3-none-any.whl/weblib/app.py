"""
Classe principale WebApp per WebLib
"""

import os
from typing import Dict, Any, Optional, Callable
from flask import Flask, request, make_response, send_from_directory
from .routing import Router, Request, Response
from .html import HtmlElement


class WebApp:
    """Classe principale per creare webapp con WebLib"""
    
    def __init__(self, name: str = __name__, static_folder: str = "static", 
                 template_folder: str = "templates"):
        self.name = name
        self.static_folder = static_folder
        self.template_folder = template_folder
        self.router = Router()
        self.flask_app = Flask(name, static_folder=static_folder, template_folder=template_folder)
        self.middleware: list[Callable] = []
        
        # Setup delle route Flask per gestire tutte le richieste
        self._setup_flask_routes()
    
    def _setup_flask_routes(self):
        """Configura le route Flask per intercettare tutte le richieste"""
        @self.flask_app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD'])
        @self.flask_app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD'])
        def catch_all(path=''):
            # Crea un oggetto Request personalizzato
            weblib_request = Request(
                method=request.method,
                path='/' + path if path else '/',
                query_string=request.query_string.decode('utf-8'),
                headers=dict(request.headers),
                form_data=dict(request.form)
            )
            
            # Applica middleware
            for middleware in self.middleware:
                weblib_request = middleware(weblib_request) or weblib_request
            
            # Gestisce la richiesta tramite il router
            response = self.router.dispatch(weblib_request)
            
            # Converte la risposta WebLib in risposta Flask
            flask_response = make_response(response.content, response.status_code)
            
            # Imposta gli headers
            for key, value in response.headers.items():
                flask_response.headers[key] = value
            
            return flask_response
    
    def set_static_folder(self, path: str):
        """Imposta la cartella per i file statici"""
        self.static_folder = path
        self.flask_app.static_folder = path
    
    def add_middleware(self, middleware: Callable):
        """Aggiunge un middleware"""
        self.middleware.append(middleware)
    
    def route(self, pattern: str, methods: Optional[list] = None):
        """Decorator per aggiungere route"""
        return self.router.route(pattern, methods)
    
    def get(self, pattern: str):
        """Decorator per route GET"""
        return self.router.get(pattern)
    
    def post(self, pattern: str):
        """Decorator per route POST"""
        return self.router.post(pattern)
    
    def put(self, pattern: str):
        """Decorator per route PUT"""
        return self.router.put(pattern)
    
    def delete(self, pattern: str):
        """Decorator per route DELETE"""
        return self.router.delete(pattern)
    
    def error_handler(self, status_code: int):
        """Decorator per gestori di errore"""
        return self.router.error_handler(status_code)
    
    def serve_static(self, filename: str):
        """Serve file statici"""
        return send_from_directory(self.static_folder, filename)
    
    def add_static_route(self, route_pattern: str = "/static/<path:filename>"):
        """Aggiunge una route per servire file statici"""
        @self.flask_app.route(route_pattern)
        def static_files(filename):
            return self.serve_static(filename)
    
    def run(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = True):
        """Avvia l'applicazione"""
        print(f"🚀 WebLib app starting on http://{host}:{port}")
        self.flask_app.run(host=host, port=port, debug=debug)
    
    def create_page(self, title: str = "WebLib App", 
                   css_links: Optional[list[str]] = None,
                   js_links: Optional[list[str]] = None) -> 'PageBuilder':
        """Crea un helper per costruire pagine HTML complete"""
        return PageBuilder(title, css_links, js_links)


class PageBuilder:
    """Helper per costruire pagine HTML complete"""
    
    def __init__(self, title: str = "WebLib App", 
                 css_links: Optional[list[str]] = None,
                 js_links: Optional[list[str]] = None):
        self.title = title
        self.css_links = css_links or []
        self.js_links = js_links or []
        self.body_content = []
        self.head_content = []
    
    def add_css(self, href: str) -> 'PageBuilder':
        """Aggiunge un link CSS"""
        self.css_links.append(href)
        return self
    
    def add_js(self, src: str) -> 'PageBuilder':
        """Aggiunge un link JavaScript"""
        self.js_links.append(src)
        return self
    
    def add_to_head(self, element: HtmlElement) -> 'PageBuilder':
        """Aggiunge contenuto al head"""
        self.head_content.append(element)
        return self
    
    def add_to_body(self, element: HtmlElement) -> 'PageBuilder':
        """Aggiunge contenuto al body"""
        self.body_content.append(element)
        return self
    
    def build(self) -> HtmlElement:
        """Costruisce la pagina HTML completa"""
        from .html import Html, Head, Body, Title, Meta, Link, Script
        
        # Costruisce il head
        head_elements = [
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Title(self.title)
        ]
        
        # Aggiunge i CSS
        for css_href in self.css_links:
            head_elements.append(Link(rel="stylesheet", href=css_href))
        
        # Aggiunge contenuto personalizzato del head
        head_elements.extend(self.head_content)
        
        head = Head(head_elements)
        
        # Costruisce il body con il contenuto
        body = Body(self.body_content)
        
        # Aggiunge i JavaScript alla fine del body
        for js_src in self.js_links:
            body.add_child(Script(src=js_src))
        
        # Costruisce l'HTML completo
        html = Html([head, body])
        html.set_attribute('lang', 'it')
        
        return html
