"""
Configurazione e utilità per WebLib
"""

import os
from typing import Dict, Any

class Config:
    """Classe per gestire la configurazione dell'applicazione"""
    
    # Configurazioni predefinite
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 5000
    DEFAULT_DEBUG = True
    
    # Path predefiniti
    DEFAULT_STATIC_FOLDER = "static"
    DEFAULT_TEMPLATE_FOLDER = "templates"
    
    # Configurazioni Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'weblib-secret-key-change-in-production'
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Crea una configurazione da un dizionario"""
        config = cls()
        for key, value in config_dict.items():
            setattr(config, key, value)
        return config
    
    @classmethod
    def from_env(cls, prefix: str = 'WEBLIB_') -> 'Config':
        """Crea una configurazione dalle variabili d'ambiente"""
        config = cls()
        
        # Legge le variabili d'ambiente con il prefisso specificato
        for key, value in os.environ.items():
            if key.startswith(prefix):
                attr_name = key[len(prefix):].lower()
                
                # Converte i valori appropriati
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                
                setattr(config, attr_name, value)
        
        return config


# Utilità per CSS comuni
class CSSClasses:
    """Classi CSS comuni per Bootstrap e altri framework"""
    
    # Bootstrap: Layout
    CONTAINER = "container"
    CONTAINER_FLUID = "container-fluid"
    ROW = "row"
    
    # Bootstrap: Grid
    COL = "col"
    COL_MD_1 = "col-md-1"
    COL_MD_2 = "col-md-2"
    COL_MD_3 = "col-md-3"
    COL_MD_4 = "col-md-4"
    COL_MD_5 = "col-md-5"
    COL_MD_6 = "col-md-6"
    COL_MD_7 = "col-md-7"
    COL_MD_8 = "col-md-8"
    COL_MD_9 = "col-md-9"
    COL_MD_10 = "col-md-10"
    COL_MD_11 = "col-md-11"
    COL_MD_12 = "col-md-12"
    
    # Bootstrap: Spacing
    MT_1 = "mt-1"
    MT_2 = "mt-2"
    MT_3 = "mt-3"
    MT_4 = "mt-4"
    MT_5 = "mt-5"
    MB_1 = "mb-1"
    MB_2 = "mb-2"
    MB_3 = "mb-3"
    MB_4 = "mb-4"
    MB_5 = "mb-5"
    MS_1 = "ms-1"
    MS_2 = "ms-2"
    MS_3 = "ms-3"
    ME_1 = "me-1"
    ME_2 = "me-2"
    ME_3 = "me-3"
    P_1 = "p-1"
    P_2 = "p-2"
    P_3 = "p-3"
    P_4 = "p-4"
    P_5 = "p-5"
    PY_1 = "py-1"
    PY_2 = "py-2"
    PY_3 = "py-3"
    PY_4 = "py-4"
    PY_5 = "py-5"
    
    # Bootstrap: Text
    TEXT_CENTER = "text-center"
    TEXT_LEFT = "text-left"
    TEXT_RIGHT = "text-right"
    TEXT_START = "text-start"
    TEXT_END = "text-end"
    TEXT_PRIMARY = "text-primary"
    TEXT_SECONDARY = "text-secondary"
    TEXT_SUCCESS = "text-success"
    TEXT_DANGER = "text-danger"
    TEXT_WARNING = "text-warning"
    TEXT_INFO = "text-info"
    TEXT_LIGHT = "text-light"
    TEXT_DARK = "text-dark"
    TEXT_MUTED = "text-muted"
    
    # Bootstrap: Buttons
    BTN = "btn"
    BTN_PRIMARY = "btn-primary"
    BTN_SECONDARY = "btn-secondary"
    BTN_SUCCESS = "btn-success"
    BTN_DANGER = "btn-danger"
    BTN_WARNING = "btn-warning"
    BTN_INFO = "btn-info"
    BTN_LIGHT = "btn-light"
    BTN_DARK = "btn-dark"
    BTN_LG = "btn-lg"
    BTN_SM = "btn-sm"
    BTN_OUTLINE_PRIMARY = "btn-outline-primary"
    BTN_OUTLINE_SECONDARY = "btn-outline-secondary"
    BTN_OUTLINE_SUCCESS = "btn-outline-success"
    BTN_OUTLINE_DANGER = "btn-outline-danger"
    BTN_OUTLINE_WARNING = "btn-outline-warning"
    BTN_OUTLINE_INFO = "btn-outline-info"
    
    # Bootstrap: Cards
    CARD = "card"
    CARD_BODY = "card-body"
    CARD_HEADER = "card-header"
    CARD_FOOTER = "card-footer"
    CARD_TITLE = "card-title"
    CARD_TEXT = "card-text"
    
    # Bootstrap: Forms
    FORM_GROUP = "form-group"
    FORM_CONTROL = "form-control"
    FORM_CONTROL_LG = "form-control-lg"
    FORM_CONTROL_SM = "form-control-sm"
    FORM_LABEL = "form-label"
    FORM_SELECT = "form-select"
    
    # Bootstrap: Alerts
    ALERT = "alert"
    ALERT_PRIMARY = "alert-primary"
    ALERT_SECONDARY = "alert-secondary"
    ALERT_SUCCESS = "alert-success"
    ALERT_DANGER = "alert-danger"
    ALERT_WARNING = "alert-warning"
    ALERT_INFO = "alert-info"
    
    # Bootstrap: Navigation
    NAVBAR = "navbar"
    NAVBAR_BRAND = "navbar-brand"
    NAVBAR_EXPAND_LG = "navbar-expand-lg"
    NAVBAR_LIGHT = "navbar-light"
    NAVBAR_DARK = "navbar-dark"
    NAV_LINK = "nav-link"
    
    # Bootstrap: Display
    DISPLAY_1 = "display-1"
    DISPLAY_2 = "display-2"
    DISPLAY_3 = "display-3"
    DISPLAY_4 = "display-4"
    DISPLAY_5 = "display-5"
    DISPLAY_6 = "display-6"
    
    # Bootstrap: Flexbox
    D_FLEX = "d-flex"
    D_INLINE_FLEX = "d-inline-flex"
    FLEX_ROW = "flex-row"
    FLEX_COLUMN = "flex-column"
    JUSTIFY_CONTENT_START = "justify-content-start"
    JUSTIFY_CONTENT_END = "justify-content-end"
    JUSTIFY_CONTENT_CENTER = "justify-content-center"
    JUSTIFY_CONTENT_BETWEEN = "justify-content-between"
    JUSTIFY_CONTENT_AROUND = "justify-content-around"
    ALIGN_ITEMS_START = "align-items-start"
    ALIGN_ITEMS_END = "align-items-end"
    ALIGN_ITEMS_CENTER = "align-items-center"
    ALIGN_ITEMS_STRETCH = "align-items-stretch"
    
    # Lead
    LEAD = "lead"
    
    # Bootstrap: Float
    FLOAT_START = "float-start"
    FLOAT_END = "float-end"
    FLOAT_LEFT = "float-left"
    FLOAT_RIGHT = "float-right"
    
    # Bootstrap: Lists
    LIST_UNSTYLED = "list-unstyled"
    LIST_INLINE = "list-inline"
    LIST_INLINE_ITEM = "list-inline-item"


# Middleware comuni
def cors_middleware(request):
    """Middleware per gestire CORS"""
    # Qui potresti implementare la logica CORS
    # Per ora è un placeholder
    return request


def logging_middleware(request):
    """Middleware per il logging delle richieste"""
    print(f"📥 {request.method} {request.path}")
    return request


def auth_middleware(request):
    """Middleware per l'autenticazione (esempio)"""
    # Esempio di middleware di autenticazione
    # In un'applicazione reale, controlleresti token, sessioni, etc.
    if request.path.startswith('/admin'):
        # Simula controllo autenticazione
        pass
    return request


# Template predefiniti
def create_basic_html_template(title: str = "WebLib App", 
                              css_links: list = None,
                              js_links: list = None) -> str:
    """Crea un template HTML di base"""
    css_links = css_links or ["https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"]
    js_links = js_links or ["https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"]
    
    css_tags = "\n".join([f'    <link rel="stylesheet" href="{link}">' for link in css_links])
    js_tags = "\n".join([f'    <script src="{link}"></script>' for link in js_links])
    
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
{css_tags}
</head>
<body>
    {{{{ content }}}}
{js_tags}
</body>
</html>"""


# Validatori di form
class FormValidator:
    """Utilità per validare dati di form"""
    
    @staticmethod
    def is_email(email: str) -> bool:
        """Validazione email semplice"""
        return "@" in email and "." in email.split("@")[-1]
    
    @staticmethod
    def is_not_empty(value: str) -> bool:
        """Controlla se un valore non è vuoto"""
        return bool(value and value.strip())
    
    @staticmethod
    def min_length(value: str, min_len: int) -> bool:
        """Controlla la lunghezza minima"""
        return len(value.strip()) >= min_len
    
    @staticmethod
    def max_length(value: str, max_len: int) -> bool:
        """Controlla la lunghezza massima"""
        return len(value.strip()) <= max_len
