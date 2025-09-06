"""
Core WebApp class for WebLib, now powered by Starlette for ASGI support.
"""

import os
from typing import Dict, Any, Optional, Callable
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.requests import Request as StarletteRequest
from starlette.websockets import WebSocket
import uvicorn

from .routing import Router, Request, Response
from .html import HtmlElement
from .components import LiveComponent
import json


class WebApp:
    """Main class for creating web applications with WebLib, using an ASGI-native engine."""
    
    def __init__(self, name: str = __name__, static_folder: str = "static"):
        self.name = name
        self.static_folder = static_folder
        self.router = Router()
        self.asgi_app = Starlette()
        self.middleware: list[Callable] = []
        self._live_components: Dict[str, LiveComponent] = {}
        
        # Add the main request handler and the WebSocket endpoint
        self.asgi_app.add_route("/{path:path}", self._handle_request, methods=["GET", "POST"])
        self.asgi_app.add_websocket_route("/ws", self._websocket_endpoint)

    async def _handle_request(self, request: StarletteRequest) -> HTMLResponse:
        try:
            print(f"Incoming request: {request.method} {request.url.path}")
            print(f"Request cookies: {request.cookies}")

            form_data = await request.form()

            # Parsing numerico robusto
            def _coerce_number(s: str):
                if not isinstance(s, str):
                    return s
                raw = s.strip()
                if not raw:
                    return s
                # prova int (supporta segno)
                try:
                    if raw.startswith(('+', '-')):
                        int(raw)
                        return int(raw)
                    # anche "0123"
                    if raw.isdigit():
                        return int(raw)
                except Exception:
                    pass
                # prova float (supporta segno e punto decimale)
                try:
                    return float(raw)
                except Exception:
                    return s

            clean_form_data = {}
            for key, value in form_data.items():
                clean_form_data[key] = _coerce_number(value)

            weblib_request = Request(
                method=request.method,
                path=request.url.path,
                query_string=request.url.query,
                headers=dict(request.headers),
                form_data=clean_form_data,
                cookies=request.cookies
            )

            for middleware_func in self.middleware:
                weblib_request = middleware_func(weblib_request) or weblib_request

            response = self.router.dispatch(weblib_request)
            
            if 'application/json' in response.headers.get('Content-Type', ''):
                starlette_response = JSONResponse(content=response.content, status_code=response.status_code, headers=response.headers)
            else:
                starlette_response = HTMLResponse(content=response.content, status_code=response.status_code, headers=response.headers)

            print(f"Response cookies: {response.cookies}")
            for cookie in response.cookies:
                print(f"Setting cookie: {cookie['key']} = {cookie['value'][:20]}...")
                starlette_response.set_cookie(
                    key=cookie['key'],
                    value=cookie['value'],
                    max_age=cookie.get('max_age'),
                    expires=cookie.get('expires'),
                    path=cookie.get('path', '/'),
                    domain=cookie.get('domain'),
                    secure=cookie.get('secure', False),
                    httponly=cookie.get('httponly', False),
                    samesite=cookie.get('samesite', 'lax')
                )
            return starlette_response
        
        except Exception as e:
            import traceback
            import sys
            import inspect
            
            # Ottieni informazioni dettagliate sull'errore
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            
            # Ottieni più informazioni sui frame del traceback
            frames = inspect.getinnerframes(exc_traceback)
            detailed_frames = []
            
            for frame in frames:
                frame_info = {
                    "filename": frame.filename,
                    "lineno": frame.lineno,
                    "function": frame.function,
                    "code_context": frame.code_context[0].strip() if frame.code_context else "N/A",
                    "locals": {}
                }
                
                # Aggiungi le variabili locali più rilevanti (evita oggetti troppo complessi)
                for key, value in frame.frame.f_locals.items():
                    # Skip complex objects, focusing on builtins and simple types
                    if key.startswith("__") or isinstance(value, (dict, list)) and len(str(value)) > 100:
                        continue
                    try:
                        if isinstance(value, (int, float, str, bool, type(None))):
                            frame_info["locals"][key] = f"{repr(value)} ({type(value).__name__})"
                        else:
                            frame_info["locals"][key] = f"{type(value).__name__}"
                    except:
                        frame_info["locals"][key] = "<<error displaying value>>"
                
                detailed_frames.append(frame_info)
            
            # Log l'errore con informazioni dettagliate
            error_msg = f"ERROR IN REQUEST HANDLING: {str(e)}\n{tb_str}"
            print(error_msg)
            print("\nDETAILED FRAME INFORMATION:")
            for i, frame in enumerate(detailed_frames):
                print(f"\nFrame {i}: {frame['filename']}:{frame['lineno']} in {frame['function']}")
                print(f"Code: {frame['code_context']}")
                print("Locals:")
                for k, v in frame['locals'].items():
                    print(f"  {k} = {v}")
            
            # Generate a more detailed error page
            frames_html = ""
            for i, frame in enumerate(detailed_frames):
                locals_html = "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in frame['locals'].items()])
                frames_html += f"""
                <div class="frame-info">
                    <h4>Frame {i}: {frame['filename']}:{frame['lineno']} in {frame['function']}</h4>
                    <p><strong>Code:</strong> <code>{frame['code_context']}</code></p>
                    <div class="locals-table">
                        <details>
                            <summary>Local Variables</summary>
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Value</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {locals_html}
                                </tbody>
                            </table>
                        </details>
                    </div>
                </div>
                """
            
            return HTMLResponse(
                content=f"""
                <html>
                    <head>
                        <title>Error 500</title>
                        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                        <style>
                            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
                            h1 {{ color: #d9534f; }}
                            h2 {{ color: #5bc0de; margin-top: 20px; }}
                            h4 {{ color: #333; margin-top: 15px; background-color: #f8f9fa; padding: 10px; border-radius: 5px; }}
                            pre {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                            code {{ background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
                            .error-details {{ background-color: #f5f5f5; padding: 15px; border-left: 5px solid #d9534f; margin-bottom: 20px; }}
                            .debug-info {{ margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px; }}
                            .frame-info {{ margin-bottom: 20px; border: 1px solid #eee; padding: 10px; border-radius: 5px; }}
                            .locals-table {{ margin-top: 10px; }}
                            .locals-table table {{ font-size: 0.9em; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>Error 500 - Internal Server Error</h1>
                            <div class="error-details">
                                <p>An unexpected error occurred:</p>
                                <pre><strong>{str(e)}</strong></pre>
                            </div>
                            
                            <h2>Traceback:</h2>
                            <pre>{tb_str}</pre>
                            
                            <div class="debug-info">
                                <h2>Enhanced Debug Information:</h2>
                                
                                <h3>Error Type:</h3>
                                <pre>{exc_type.__name__}</pre>
                                
                                <h3>Request Details:</h3>
                                <pre>
Method: {request.method}
Path: {request.url.path}
Query: {request.url.query}
Headers: {dict(request.headers)}
                                </pre>
                                
                                <h3>Traceback Frames with Local Variables:</h3>
                                {frames_html}
                            </div>
                        </div>
                        
                        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
                    </body>
                </html>
                """,
                status_code=500
            )

    def add_middleware(self, middleware: Callable):
        """Adds a middleware function."""
        self.middleware.append(middleware)

    def route(self, pattern: str, methods: Optional[list] = None):
        """Decorator to add a route."""
        return self.router.route(pattern, methods)

    def get(self, pattern: str):
        """Decorator for GET routes."""
        return self.router.get(pattern)

    def post(self, pattern: str):
        """Decorator for POST routes."""
        return self.router.post(pattern)

    def put(self, pattern: str):
        """Decorator for PUT routes."""
        return self.router.put(pattern)

    def delete(self, pattern: str):
        """Decorator for DELETE routes."""
        return self.router.delete(pattern)
        
    def page(self, pattern: str):
        """Decorator to register a page that may contain LiveComponents."""
        def decorator(handler: Callable):
            @self.router.get(pattern)
            def wrapper(*args, **kwargs):
                # Execute the user's page function to get the component
                component = handler(*args, **kwargs)
                
                # If it's a LiveComponent, register it for WebSocket communication
                if isinstance(component, LiveComponent):
                    self._live_components[component.id] = component
                
                # Render the component to HTML
                # The component's render method includes the JS bridge
                html_content = component.render().render()
                return Response(html_content)
            return wrapper
        return decorator

    async def _websocket_endpoint(self, websocket: WebSocket):
        """Handles the lifecycle of all WebSocket connections."""
        await websocket.accept()
        try:
            while True:
                message = await websocket.receive_json()
                msg_type = message.get("type")
                component_id = message.get("component_id")

                if not component_id or component_id not in self._live_components:
                    continue

                component = self._live_components[component_id]

                if msg_type == "mount":
                    # Associate the websocket with the component instance
                    await component.mount(websocket)
                elif msg_type == "event":
                    # Handle the incoming event
                    await component.handle_event(message.get("event", {}))

        except Exception as e:
            print(f"WebSocket Error: {e}")
        finally:
            # Clean up on disconnect
            # Find which component this websocket was connected to and remove it
            for comp_id, comp in list(self._live_components.items()):
                if comp.websocket == websocket:
                    del self._live_components[comp_id]
                    break
            print("WebSocket connection closed.")

    def run(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = True):
        """
        Starts the ASGI application using uvicorn.
        
        Args:
            host: The host to bind to
            port: The port to bind to
            debug: Whether to enable debug mode
        """
        print(f"🚀 WebLib ASGI app starting on http://{host}:{port}")
        
        # Explicitly set socket options to handle socket reuse
        uvicorn_config = uvicorn.Config(
            app=self.asgi_app, 
            host=host, 
            port=port, 
            log_level="info" if debug else "warning"
        )
        server = uvicorn.Server(config=uvicorn_config)
        
        try:
            server.run()
        except KeyboardInterrupt:
            print("\nServer shutdown requested by user. Exiting...")
        except Exception as e:
            print(f"\nError running server: {str(e)}")

    def create_page(self, title: str = "WebLib App", 
                   css_links: Optional[list[str]] = None,
                   js_links: Optional[list[str]] = None) -> 'PageBuilder':
        """Creates a helper for building complete HTML pages."""
        return PageBuilder(title, css_links, js_links)


class PageBuilder:
    """Helper for building complete HTML pages."""
    
    def __init__(self, title: str = "WebLib App", 
                 css_links: Optional[list[str]] = None,
                 js_links: Optional[list[str]] = None):
        self.title = title
        self.css_links = css_links or []
        self.js_links = js_links or []
        self.js_scripts = []
        self.body_content = []
        self.head_content = []
    
    def add_css(self, href: str) -> 'PageBuilder':
        """Adds a CSS link."""
        self.css_links.append(href)
        return self
    
    def add_js(self, src: str) -> 'PageBuilder':
        """Adds a JavaScript link."""
        self.js_links.append(src)
        return self

    def add_js_string(self, script: str) -> 'PageBuilder':
        """Adds an inline JavaScript string."""
        self.js_scripts.append(script)
        return self
    
    def add_to_head(self, element: HtmlElement) -> 'PageBuilder':
        """Adds content to the head."""
        self.head_content.append(element)
        return self
    
    def add_to_body(self, element: HtmlElement) -> 'PageBuilder':
        """Adds content to the body."""
        self.body_content.append(element)
        return self
    
    def build(self) -> HtmlElement:
        """Builds the complete HTML page."""
        from .html import Html, Head, Body, Title, Meta, Link, Script
        
        # Build the head
        head_elements = [
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Title(self.title)
        ]
        
        # Add CSS links
        for css_href in self.css_links:
            head_elements.append(Link(rel="stylesheet", href=css_href))
        
        # Add custom head content
        head_elements.extend(self.head_content)
        
        head = Head(head_elements)
        
        # Build the body with content
        body = Body(self.body_content)
        
        # Add JavaScript links to the end of the body
        for js_src in self.js_links:
            body.add_child(Script(src=js_src))

        for script in self.js_scripts:
            body.add_child(Script(script))
        
        # Build the complete HTML
        html = Html([head, body])
        html.set_attribute('lang', 'en')
        
        return html
