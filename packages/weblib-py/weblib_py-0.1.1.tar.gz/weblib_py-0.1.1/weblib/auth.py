"""
Sistema di Session Management e Autenticazione per WebLib
"""

import json
import hashlib
import secrets
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
from .routing import Request, Response


class Session:
    """Classe per gestire le sessioni utente"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or self._generate_session_id()
        self.data = {}
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.is_new = True
    
    def _generate_session_id(self) -> str:
        """Genera un ID sessione sicuro"""
        return secrets.token_urlsafe(32)
    
    def get(self, key: str, default=None):
        """Ottiene un valore dalla sessione"""
        self.last_accessed = time.time()
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Imposta un valore nella sessione"""
        self.data[key] = value
        self.last_accessed = time.time()
    
    def delete(self, key: str):
        """Rimuove un valore dalla sessione"""
        if key in self.data:
            del self.data[key]
        self.last_accessed = time.time()
    
    def clear(self):
        """Cancella tutti i dati della sessione"""
        self.data.clear()
        self.last_accessed = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte la sessione in dizionario per serializzazione"""
        return {
            'session_id': self.session_id,
            'data': self.data,
            'created_at': self.created_at,
            'last_accessed': self.last_accessed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Crea una sessione da dizionario"""
        session = cls(data['session_id'])
        session.data = data.get('data', {})
        session.created_at = data.get('created_at', time.time())
        session.last_accessed = data.get('last_accessed', time.time())
        session.is_new = False
        return session


class SessionStore:
    """Store per le sessioni (implementazione in memoria)"""
    
    def __init__(self, max_age: int = 3600):  # 1 ora default
        self.sessions = {}
        self.max_age = max_age
    
    def get(self, session_id: str) -> Optional[Session]:
        """Ottiene una sessione"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            # Controlla scadenza
            if time.time() - session.last_accessed > self.max_age:
                del self.sessions[session_id]
                return None
            return session
        return None
    
    def save(self, session: Session):
        """Salva una sessione"""
        self.sessions[session.session_id] = session
    
    def delete(self, session_id: str):
        """Cancella una sessione"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup(self):
        """Rimuove le sessioni scadute"""
        current_time = time.time()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if current_time - session.last_accessed > self.max_age
        ]
        for sid in expired_sessions:
            del self.sessions[sid]


class User:
    """Classe base per rappresentare un utente"""
    
    def __init__(self, user_id: str, username: str, email: str = None, **kwargs):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.data = kwargs
        self.is_authenticated = True
    
    def get(self, key: str, default=None):
        """Ottiene un attributo utente"""
        return self.data.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte l'utente in dizionario"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'data': self.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Crea un utente da dizionario"""
        return cls(
            user_id=data['user_id'],
            username=data['username'],
            email=data.get('email'),
            **data.get('data', {})
        )


class AuthManager:
    """Gestore dell'autenticazione"""
    
    def __init__(self):
        self.users = {}  # user_id -> User
        self.credentials = {}  # username -> password_hash
    
    def hash_password(self, password: str) -> str:
        """Crea hash della password"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', 
                                      password.encode('utf-8'), 
                                      salt.encode('utf-8'), 
                                      100000)
        return f"{salt}:{pwd_hash.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica password contro hash"""
        try:
            salt, pwd_hash = password_hash.split(':')
            return pwd_hash == hashlib.pbkdf2_hmac('sha256',
                                                   password.encode('utf-8'),
                                                   salt.encode('utf-8'),
                                                   100000).hex()
        except:
            return False
    
    def register_user(self, username: str, password: str, email: str = None, **kwargs) -> User:
        """Registra un nuovo utente"""
        if username in self.credentials:
            raise ValueError("Username already exists")
        
        user_id = secrets.token_urlsafe(16)
        user = User(user_id, username, email, **kwargs)
        
        self.users[user_id] = user
        self.credentials[username] = self.hash_password(password)
        
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Autentica un utente"""
        if username not in self.credentials:
            return None
        
        password_hash = self.credentials[username]
        if not self.verify_password(password, password_hash):
            return None
        
        # Trova l'utente
        for user in self.users.values():
            if user.username == username:
                return user
        
        return None
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Ottiene un utente per ID"""
        return self.users.get(user_id)


class AuthMiddleware:
    """Middleware per gestire autenticazione e sessioni"""
    
    def __init__(self, session_store: SessionStore = None, auth_manager: AuthManager = None):
        self.session_store = session_store or SessionStore()
        self.auth_manager = auth_manager or AuthManager()
        self.cookie_name = 'weblib_session'
    
    def process_request(self, request: Request) -> Request:
        """Processa la richiesta aggiungendo sessione e utente"""
        # Ottieni session ID dai cookie
        session_id = self._get_session_id_from_cookies(request)
        
        # Carica o crea sessione
        if session_id:
            session = self.session_store.get(session_id)
        else:
            session = None
        
        if not session:
            session = Session()
            session.is_new = True
        
        request.session = session
        
        # Carica utente se autenticato
        user_id = session.get('user_id')
        if user_id:
            user = self.auth_manager.get_user(user_id)
            request.user = user
        else:
            request.user = None
        
        return request
    
    def process_response(self, request: Request, response: Response) -> Response:
        """Processa la risposta salvando sessione e cookie"""
        if hasattr(request, 'session'):
            # Salva sessione
            self.session_store.save(request.session)
            
            # Imposta cookie se nuova sessione o modificata
            if request.session.is_new or request.session.data:
                self._set_session_cookie(response, request.session.session_id)
        
        return response
    
    def _get_session_id_from_cookies(self, request: Request) -> Optional[str]:
        """Estrae session ID dai cookie"""
        # Implementazione semplice - in un'app reale useresti il parsing dei cookie
        # Per ora simuliamo con gli headers
        cookie_header = getattr(request, 'cookies', {})
        return cookie_header.get(self.cookie_name)
    
    def _set_session_cookie(self, response: Response, session_id: str):
        """Imposta il cookie di sessione"""
        # Aggiunge header Set-Cookie alla risposta
        if not hasattr(response, 'headers'):
            response.headers = {}
        response.headers['Set-Cookie'] = f"{self.cookie_name}={session_id}; Path=/; HttpOnly"
    
    def login_user(self, request: Request, user: User):
        """Effettua login dell'utente"""
        request.session.set('user_id', user.user_id)
        request.session.set('username', user.username)
        request.user = user
    
    def logout_user(self, request: Request):
        """Effettua logout dell'utente"""
        request.session.delete('user_id')
        request.session.delete('username')
        request.user = None


# Decoratori per l'autenticazione
def login_required(redirect_url: str = '/login'):
    """Decorator che richiede login"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(request: Request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user:
                # Redirect a login (in un'app reale)
                return Response(
                    content=f'<script>window.location.href="{redirect_url}";</script>',
                    status_code=401
                )
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def permission_required(permission: str):
    """Decorator che richiede un permesso specifico"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(request: Request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user:
                return Response(content="Unauthorized", status_code=401)
            
            # Controlla permesso (implementazione base)
            user_permissions = request.user.get('permissions', [])
            if permission not in user_permissions:
                return Response(content="Forbidden", status_code=403)
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(func: Callable):
    """Decorator che richiede privilegi admin"""
    @wraps(func)
    def wrapper(request: Request, *args, **kwargs):
        if not hasattr(request, 'user') or not request.user:
            return Response(content="Unauthorized", status_code=401)
        
        is_admin = request.user.get('is_admin', False)
        if not is_admin:
            return Response(content="Admin access required", status_code=403)
        
        return func(request, *args, **kwargs)
    return wrapper


# Utilità per form di login
def create_login_form():
    """Crea un form di login base"""
    from .forms import FormValidator, StringField, EmailField
    
    class LoginForm(FormValidator):
        username = StringField(required=True, placeholder="Username")
        password = StringField(required=True, placeholder="Password")
        
        def render_login_form(self, action="/login", method="POST"):
            """Renderizza form di login personalizzato"""
            from .html import Form, Div, Button, H2
            from .config import CSSClasses
            
            content = [
                H2("Login", classes=[CSSClasses.TEXT_CENTER, CSSClasses.MB_4]),
                self.render_field('username', 'Username'),
                self.render_field('password', 'Password'),
                Button("Login", 
                      button_type="submit",
                      classes=[CSSClasses.BTN, CSSClasses.BTN_PRIMARY, CSSClasses.W_100])
            ]
            
            return Form(content, action=action, method=method, 
                       classes=[CSSClasses.CONTAINER, "mt-5"])
    
    return LoginForm()


def create_register_form():
    """Crea un form di registrazione base"""
    from .forms import FormValidator, StringField, EmailField, ValidationError
    
    class RegisterForm(FormValidator):
        username = StringField(required=True, min_length=3, placeholder="Username")
        email = EmailField(required=True, placeholder="Email")
        password = StringField(required=True, min_length=6, placeholder="Password")
        confirm_password = StringField(required=True, placeholder="Confirm Password")
        
        def clean(self):
            """Validazione personalizzata"""
            password = self.data.get('password')
            confirm_password = self.data.get('confirm_password')
            
            if password != confirm_password:
                raise ValidationError("Passwords do not match")
    
    return RegisterForm()
