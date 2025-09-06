"""
WebLib v2.0 - Framework Python per Web Applications
Libreria completa con componenti, forms, auth, database e charts
Supporto multi-framework CSS: Bootstrap, Tailwind, Bulma
"""

# Basic imports
from .html import *
from .app import WebApp, PageBuilder
from .routing import Router, Request, Response
from .config import Config

# Database ORM
from .orm import Database, Model, QuerySet, Field

# Framework CSS Multi-Support
from .css_frameworks import (
    CSSFramework, BootstrapFramework, TailwindFramework, BulmaFramework, 
    FrameworkManager, DEFAULT_FRAMEWORK
)

# Charts
from .charts import (
    ChartJS, PlotlyJS, ApexCharts, ChartBuilder, ChartPage,
    quick_line_chart, quick_bar_chart, quick_pie_chart, SAMPLE_DATA
)

# Nuove funzionalità v2.0
from .components import *
from .forms import *
from .auth import *

__version__ = "2.0.0"
__author__ = "WebLib Team"

# Framework CSS attivo (default Bootstrap)
_current_framework = DEFAULT_FRAMEWORK

def set_css_framework(framework_name: str):
    """Imposta il framework CSS attivo"""
    global _current_framework
    _current_framework = FrameworkManager.get_framework(framework_name)
    return _current_framework

def get_css_framework() -> CSSFramework:
    """Ottieni il framework CSS attivo"""
    return _current_framework

# CSS Classes dinamiche basate sul framework attivo
class CSSClasses:
    """Classi CSS dinamiche che si adattano al framework attivo"""
    
    @property
    def CONTAINER(self): return get_css_framework().CONTAINER
    
    @property
    def CONTAINER_FLUID(self): return get_css_framework().CONTAINER
    
    @property
    def ROW(self): return get_css_framework().ROW
    
    @property
    def COL(self): return get_css_framework().COL
    
    @property
    def COL_AUTO(self): return get_css_framework().COL_AUTO
    
    # Buttons
    @property
    def BTN(self): return get_css_framework().BTN
    
    @property
    def BTN_PRIMARY(self): return get_css_framework().BTN_PRIMARY
    
    @property
    def BTN_SECONDARY(self): return get_css_framework().BTN_SECONDARY
    
    @property
    def BTN_SUCCESS(self): return get_css_framework().BTN_SUCCESS
    
    @property
    def BTN_DANGER(self): return get_css_framework().BTN_DANGER
    
    @property
    def BTN_WARNING(self): return get_css_framework().BTN_WARNING
    
    @property
    def BTN_INFO(self): return get_css_framework().BTN_INFO
    
    # Components
    @property
    def CARD(self): return get_css_framework().CARD
    
    @property
    def CARD_HEADER(self): return get_css_framework().CARD_HEADER
    
    @property
    def CARD_BODY(self): return get_css_framework().CARD_BODY
    
    @property
    def CARD_FOOTER(self): return get_css_framework().CARD_FOOTER
    
    @property
    def ALERT(self): return get_css_framework().ALERT
    
    @property
    def NAVBAR(self): return get_css_framework().NAVBAR
    
    @property
    def MODAL(self): return get_css_framework().MODAL
    
    @property
    def BADGE(self): return get_css_framework().BADGE
    
    # Forms
    @property
    def FORM_CONTROL(self): return get_css_framework().FORM_CONTROL
    
    @property
    def FORM_GROUP(self): return get_css_framework().FORM_GROUP
    
    @property
    def FORM_LABEL(self): return get_css_framework().FORM_LABEL
    
    # Utilities
    @property
    def TEXT_CENTER(self): return get_css_framework().TEXT_CENTER
    
    @property
    def TEXT_LEFT(self): return get_css_framework().TEXT_LEFT
    
    @property
    def TEXT_RIGHT(self): return get_css_framework().TEXT_RIGHT
    
    @property
    def D_FLEX(self): return get_css_framework().D_FLEX
    
    @property
    def D_BLOCK(self): return get_css_framework().D_BLOCK
    
    @property
    def D_NONE(self): return get_css_framework().D_NONE
    
    # Backward compatibility - margins/padding
    @property
    def ME_2(self): return get_css_framework().margin(2, 'e') if hasattr(get_css_framework(), 'margin') else 'me-2'
    
    @property  
    def ME_3(self): return get_css_framework().margin(3, 'e') if hasattr(get_css_framework(), 'margin') else 'me-3'
    
    @property
    def MB_3(self): return get_css_framework().margin(3, 'b') if hasattr(get_css_framework(), 'margin') else 'mb-3'
    
    @property
    def MT_5(self): return get_css_framework().margin(5, 't') if hasattr(get_css_framework(), 'margin') else 'mt-5'
    
    # Helper methods
    def get_col_size(self, size: int, breakpoint: str = "md"):
        """Genera classe colonna con dimensione"""
        return get_css_framework().col_size(size, breakpoint)
    
    def get_color_class(self, color: str, type: str = "text"):
        """Genera classe colore"""
        return get_css_framework().get_color_class(color, type)
    
    def get_alert_class(self, type: str):
        """Genera classe alert"""
        return get_css_framework().get_alert_class(type)
    
    def get_badge_class(self, variant: str, pill: bool = False):
        """Genera classe badge"""
        return get_css_framework().get_badge_class(variant, pill)

# Istanza globale delle classi CSS
CSS = CSSClasses()

__all__ = [
    # App principale
    'WebApp',
    'Router',
    'Request',
    'Response',
    
    # Configurazione
    'Config',
    'CSSClasses',
    
    # CSS Framework functions
    'set_css_framework',
    'get_css_framework',
    'CSS',
    
    # Charts
    'ChartJS',
    'PlotlyJS', 
    'ApexCharts',
    'ChartBuilder',
    'ChartPage',
    'quick_line_chart',
    'quick_bar_chart', 
    'quick_pie_chart',
    'SAMPLE_DATA',
    
    # Elementi HTML
    'Html', 'Head', 'Body', 'Title', 'Meta', 'Link', 'Script', 'Style',
    'Div', 'Span', 'P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'A', 'Img',
    'Button', 'Input', 'Form', 'Label', 'Select', 'Option', 'Textarea',
    'Ul', 'Ol', 'Li', 'Table', 'Tr', 'Td', 'Th', 'Thead', 'Tbody',
    'Nav', 'Header', 'Footer', 'Section', 'Article', 'Aside', 'Main', 'I', 'Hr',
    
    # Database ORM
    'Database', 'Model', 'QuerySet', 'Field'
]
