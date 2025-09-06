#!/usr/bin/env python3
"""
Sistema Multi-Framework CSS per WebLib v2.0
Supporta Bootstrap, Tailwind CSS, Bulma e framework personalizzati
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union


class CSSFramework(ABC):
    """Classe base astratta per framework CSS"""
    
    def __init__(self):
        self.name = self.__class__.__name__.replace("Framework", "").lower()
        self.version = "latest"
        self.cdn_css = ""
        self.cdn_js = ""
    
    # Layout Classes
    @property
    @abstractmethod
    def CONTAINER(self) -> str: pass
    
    @property 
    @abstractmethod
    def ROW(self) -> str: pass
    
    @property
    @abstractmethod  
    def COL(self) -> str: pass
    
    @property
    @abstractmethod
    def COL_AUTO(self) -> str: pass
    
    # Grid System
    def col_size(self, size: int, breakpoint: str = "md") -> str:
        """Genera classe per colonna con dimensione specifica"""
        return f"col-{breakpoint}-{size}"
    
    # Button Classes
    @property
    @abstractmethod
    def BTN(self) -> str: pass
    
    @property
    @abstractmethod
    def BTN_PRIMARY(self) -> str: pass
    
    @property
    @abstractmethod
    def BTN_SECONDARY(self) -> str: pass
    
    @property
    @abstractmethod
    def BTN_SUCCESS(self) -> str: pass
    
    @property
    @abstractmethod
    def BTN_DANGER(self) -> str: pass
    
    @property
    @abstractmethod
    def BTN_WARNING(self) -> str: pass
    
    @property
    @abstractmethod
    def BTN_INFO(self) -> str: pass
    
    # Component Classes
    @property
    @abstractmethod
    def CARD(self) -> str: pass
    
    @property
    @abstractmethod
    def CARD_HEADER(self) -> str: pass
    
    @property
    @abstractmethod
    def CARD_BODY(self) -> str: pass
    
    @property
    @abstractmethod
    def CARD_FOOTER(self) -> str: pass
    
    @property
    @abstractmethod
    def ALERT(self) -> str: pass
    
    @property
    @abstractmethod
    def NAVBAR(self) -> str: pass
    
    @property
    @abstractmethod
    def MODAL(self) -> str: pass
    
    @property
    @abstractmethod
    def BADGE(self) -> str: pass
    
    # Form Classes
    @property
    @abstractmethod
    def FORM_CONTROL(self) -> str: pass
    
    @property
    @abstractmethod
    def FORM_GROUP(self) -> str: pass
    
    @property
    @abstractmethod
    def FORM_LABEL(self) -> str: pass
    
    # Utility Classes
    @property
    @abstractmethod
    def TEXT_CENTER(self) -> str: pass
    
    @property
    @abstractmethod
    def TEXT_LEFT(self) -> str: pass
    
    @property
    @abstractmethod
    def TEXT_RIGHT(self) -> str: pass
    
    @property
    @abstractmethod
    def D_FLEX(self) -> str: pass
    
    @property
    @abstractmethod
    def D_BLOCK(self) -> str: pass
    
    @property
    @abstractmethod
    def D_NONE(self) -> str: pass
    
    # Spacing
    def margin(self, size: int, side: Optional[str] = None) -> str:
        """Genera classe margin"""
        return f"m{''-'' + side if side else ''}-{size}"
    
    def padding(self, size: int, side: Optional[str] = None) -> str:
        """Genera classe padding"""
        return f"p{''-'' + side if side else ''}-{size}"
    
    # Colors
    @abstractmethod
    def get_color_class(self, color: str, type: str = "text") -> str:
        """Genera classe colore (text, bg, border)"""
        pass
    
    # Alert types
    @abstractmethod
    def get_alert_class(self, type: str) -> str:
        """Genera classe alert per tipo (success, danger, warning, info)"""
        pass
    
    # Badge variants
    @abstractmethod  
    def get_badge_class(self, variant: str, pill: bool = False) -> str:
        """Genera classe badge"""
        pass


class BootstrapFramework(CSSFramework):
    """Framework Bootstrap 5.x"""
    
    def __init__(self):
        super().__init__()
        self.version = "5.1.3"
        self.cdn_css = f"https://cdn.jsdelivr.net/npm/bootstrap@{self.version}/dist/css/bootstrap.min.css"
        self.cdn_js = f"https://cdn.jsdelivr.net/npm/bootstrap@{self.version}/dist/js/bootstrap.bundle.min.js"
    
    # Layout
    @property
    def CONTAINER(self) -> str: return "container"
    
    @property
    def ROW(self) -> str: return "row"
    
    @property
    def COL(self) -> str: return "col"
    
    @property
    def COL_AUTO(self) -> str: return "col-auto"
    
    def col_size(self, size: int, breakpoint: str = "md") -> str:
        return f"col-{breakpoint}-{size}"
    
    # Buttons
    @property
    def BTN(self) -> str: return "btn"
    
    @property
    def BTN_PRIMARY(self) -> str: return "btn btn-primary"
    
    @property
    def BTN_SECONDARY(self) -> str: return "btn btn-secondary"
    
    @property
    def BTN_SUCCESS(self) -> str: return "btn btn-success"
    
    @property
    def BTN_DANGER(self) -> str: return "btn btn-danger"
    
    @property
    def BTN_WARNING(self) -> str: return "btn btn-warning"
    
    @property
    def BTN_INFO(self) -> str: return "btn btn-info"
    
    # Components
    @property
    def CARD(self) -> str: return "card"
    
    @property
    def CARD_HEADER(self) -> str: return "card-header"
    
    @property
    def CARD_BODY(self) -> str: return "card-body"
    
    @property
    def CARD_FOOTER(self) -> str: return "card-footer"
    
    @property
    def ALERT(self) -> str: return "alert"
    
    @property
    def NAVBAR(self) -> str: return "navbar"
    
    @property
    def MODAL(self) -> str: return "modal"
    
    @property
    def BADGE(self) -> str: return "badge"
    
    # Forms
    @property
    def FORM_CONTROL(self) -> str: return "form-control"
    
    @property
    def FORM_GROUP(self) -> str: return "mb-3"
    
    @property
    def FORM_LABEL(self) -> str: return "form-label"
    
    # Utilities
    @property
    def TEXT_CENTER(self) -> str: return "text-center"
    
    @property
    def TEXT_LEFT(self) -> str: return "text-start"
    
    @property
    def TEXT_RIGHT(self) -> str: return "text-end"
    
    @property
    def D_FLEX(self) -> str: return "d-flex"
    
    @property
    def D_BLOCK(self) -> str: return "d-block"
    
    @property
    def D_NONE(self) -> str: return "d-none"
    
    def get_color_class(self, color: str, type: str = "text") -> str:
        return f"{type}-{color}"
    
    def get_alert_class(self, type: str) -> str:
        return f"alert alert-{type}"
    
    def get_badge_class(self, variant: str, pill: bool = False) -> str:
        classes = [f"badge bg-{variant}"]
        if pill:
            classes.append("rounded-pill")
        return " ".join(classes)


class TailwindFramework(CSSFramework):
    """Framework Tailwind CSS 3.x"""
    
    def __init__(self):
        super().__init__()
        self.version = "3.0"
        self.cdn_css = "https://cdn.tailwindcss.com"
        self.cdn_js = ""
    
    # Layout
    @property
    def CONTAINER(self) -> str: return "max-w-6xl mx-auto px-4"
    
    @property
    def ROW(self) -> str: return "flex flex-wrap -mx-2"
    
    @property
    def COL(self) -> str: return "flex-1 px-2"
    
    @property
    def COL_AUTO(self) -> str: return "flex-none px-2"
    
    def col_size(self, size: int, breakpoint: str = "md") -> str:
        # Tailwind usa frazioni: 1/12, 2/12, etc.
        fraction = f"{size}/12"
        prefix = "" if breakpoint == "xs" else f"{breakpoint}:"
        return f"{prefix}w-{fraction} px-2"
    
    # Buttons
    @property
    def BTN(self) -> str: return "px-4 py-2 rounded font-medium transition-colors"
    
    @property
    def BTN_PRIMARY(self) -> str: return "px-4 py-2 bg-blue-500 text-white rounded font-medium hover:bg-blue-600 transition-colors"
    
    @property
    def BTN_SECONDARY(self) -> str: return "px-4 py-2 bg-gray-500 text-white rounded font-medium hover:bg-gray-600 transition-colors"
    
    @property
    def BTN_SUCCESS(self) -> str: return "px-4 py-2 bg-green-500 text-white rounded font-medium hover:bg-green-600 transition-colors"
    
    @property
    def BTN_DANGER(self) -> str: return "px-4 py-2 bg-red-500 text-white rounded font-medium hover:bg-red-600 transition-colors"
    
    @property
    def BTN_WARNING(self) -> str: return "px-4 py-2 bg-yellow-500 text-white rounded font-medium hover:bg-yellow-600 transition-colors"
    
    @property
    def BTN_INFO(self) -> str: return "px-4 py-2 bg-cyan-500 text-white rounded font-medium hover:bg-cyan-600 transition-colors"
    
    # Components
    @property
    def CARD(self) -> str: return "bg-white shadow-lg rounded-lg overflow-hidden"
    
    @property
    def CARD_HEADER(self) -> str: return "px-6 py-4 bg-gray-50 border-b border-gray-200"
    
    @property
    def CARD_BODY(self) -> str: return "px-6 py-4"
    
    @property
    def CARD_FOOTER(self) -> str: return "px-6 py-4 bg-gray-50 border-t border-gray-200"
    
    @property
    def ALERT(self) -> str: return "p-4 rounded-md border-l-4"
    
    @property
    def NAVBAR(self) -> str: return "bg-white shadow-sm border-b border-gray-200"
    
    @property
    def MODAL(self) -> str: return "fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    
    @property
    def BADGE(self) -> str: return "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
    
    # Forms
    @property
    def FORM_CONTROL(self) -> str: return "block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
    
    @property
    def FORM_GROUP(self) -> str: return "mb-4"
    
    @property
    def FORM_LABEL(self) -> str: return "block text-sm font-medium text-gray-700 mb-1"
    
    # Utilities
    @property
    def TEXT_CENTER(self) -> str: return "text-center"
    
    @property
    def TEXT_LEFT(self) -> str: return "text-left"
    
    @property
    def TEXT_RIGHT(self) -> str: return "text-right"
    
    @property
    def D_FLEX(self) -> str: return "flex"
    
    @property
    def D_BLOCK(self) -> str: return "block"
    
    @property
    def D_NONE(self) -> str: return "hidden"
    
    def get_color_class(self, color: str, type: str = "text") -> str:
        color_map = {
            "primary": "blue-600",
            "secondary": "gray-600", 
            "success": "green-600",
            "danger": "red-600",
            "warning": "yellow-600",
            "info": "cyan-600"
        }
        tailwind_color = color_map.get(color, color)
        return f"{type}-{tailwind_color}"
    
    def get_alert_class(self, type: str) -> str:
        type_map = {
            "success": "bg-green-50 border-green-400 text-green-700",
            "danger": "bg-red-50 border-red-400 text-red-700", 
            "warning": "bg-yellow-50 border-yellow-400 text-yellow-700",
            "info": "bg-blue-50 border-blue-400 text-blue-700"
        }
        return f"p-4 rounded-md border-l-4 {type_map.get(type, type_map['info'])}"
    
    def get_badge_class(self, variant: str, pill: bool = False) -> str:
        variant_map = {
            "primary": "bg-blue-100 text-blue-800",
            "secondary": "bg-gray-100 text-gray-800",
            "success": "bg-green-100 text-green-800",
            "danger": "bg-red-100 text-red-800",
            "warning": "bg-yellow-100 text-yellow-800",
            "info": "bg-cyan-100 text-cyan-800"
        }
        
        base_classes = "inline-flex items-center px-2.5 py-0.5 text-xs font-medium"
        shape_class = "rounded-full" if pill else "rounded"
        color_classes = variant_map.get(variant, variant_map["primary"])
        
        return f"{base_classes} {shape_class} {color_classes}"


class BulmaFramework(CSSFramework):
    """Framework Bulma CSS"""
    
    def __init__(self):
        super().__init__()
        self.version = "0.9.4"
        self.cdn_css = f"https://cdn.jsdelivr.net/npm/bulma@{self.version}/css/bulma.min.css"
        self.cdn_js = ""
    
    # Layout
    @property
    def CONTAINER(self) -> str: return "container"
    
    @property
    def ROW(self) -> str: return "columns"
    
    @property
    def COL(self) -> str: return "column"
    
    @property
    def COL_AUTO(self) -> str: return "column is-narrow"
    
    def col_size(self, size: int, breakpoint: str = "md") -> str:
        # Bulma usa is-1, is-2, etc.
        return f"column is-{size}"
    
    # Buttons
    @property
    def BTN(self) -> str: return "button"
    
    @property
    def BTN_PRIMARY(self) -> str: return "button is-primary"
    
    @property
    def BTN_SECONDARY(self) -> str: return "button is-light"
    
    @property
    def BTN_SUCCESS(self) -> str: return "button is-success"
    
    @property
    def BTN_DANGER(self) -> str: return "button is-danger"
    
    @property
    def BTN_WARNING(self) -> str: return "button is-warning"
    
    @property
    def BTN_INFO(self) -> str: return "button is-info"
    
    # Components
    @property
    def CARD(self) -> str: return "card"
    
    @property
    def CARD_HEADER(self) -> str: return "card-header"
    
    @property
    def CARD_BODY(self) -> str: return "card-content"
    
    @property
    def CARD_FOOTER(self) -> str: return "card-footer"
    
    @property
    def ALERT(self) -> str: return "notification"
    
    @property
    def NAVBAR(self) -> str: return "navbar"
    
    @property
    def MODAL(self) -> str: return "modal"
    
    @property
    def BADGE(self) -> str: return "tag"
    
    # Forms
    @property
    def FORM_CONTROL(self) -> str: return "input"
    
    @property
    def FORM_GROUP(self) -> str: return "field"
    
    @property
    def FORM_LABEL(self) -> str: return "label"
    
    # Utilities
    @property
    def TEXT_CENTER(self) -> str: return "has-text-centered"
    
    @property
    def TEXT_LEFT(self) -> str: return "has-text-left"
    
    @property
    def TEXT_RIGHT(self) -> str: return "has-text-right"
    
    @property
    def D_FLEX(self) -> str: return "is-flex"
    
    @property
    def D_BLOCK(self) -> str: return "is-block"
    
    @property
    def D_NONE(self) -> str: return "is-hidden"
    
    def get_color_class(self, color: str, type: str = "text") -> str:
        type_prefix = "has-text" if type == "text" else f"has-{type}"
        return f"{type_prefix}-{color}"
    
    def get_alert_class(self, type: str) -> str:
        type_map = {
            "success": "notification is-success",
            "danger": "notification is-danger",
            "warning": "notification is-warning", 
            "info": "notification is-info"
        }
        return type_map.get(type, type_map["info"])
    
    def get_badge_class(self, variant: str, pill: bool = False) -> str:
        classes = [f"tag is-{variant}"]
        if pill:
            classes.append("is-rounded")
        return " ".join(classes)


class FrameworkManager:
    """Manager per framework CSS"""
    
    _frameworks = {
        "bootstrap": BootstrapFramework,
        "tailwind": TailwindFramework,
        "bulma": BulmaFramework
    }
    
    @classmethod
    def get_framework(cls, name: str) -> CSSFramework:
        """Ottieni istanza del framework"""
        if name.lower() not in cls._frameworks:
            raise ValueError(f"Framework '{name}' non supportato. Disponibili: {list(cls._frameworks.keys())}")
        
        return cls._frameworks[name.lower()]()
    
    @classmethod
    def register_framework(cls, name: str, framework_class: type):
        """Registra un nuovo framework personalizzato"""
        if not issubclass(framework_class, CSSFramework):
            raise ValueError("Il framework deve ereditare da CSSFramework")
        
        cls._frameworks[name.lower()] = framework_class
    
    @classmethod
    def list_frameworks(cls) -> List[str]:
        """Lista framework disponibili"""
        return list(cls._frameworks.keys())
    
    @classmethod
    def get_framework_info(cls, name: str) -> Dict:
        """Ottieni informazioni su un framework"""
        framework = cls.get_framework(name)
        return {
            "name": framework.name,
            "version": framework.version,
            "cdn_css": framework.cdn_css,
            "cdn_js": framework.cdn_js
        }


# Framework di default
DEFAULT_FRAMEWORK = BootstrapFramework()


if __name__ == "__main__":
    print("🧪 Test Framework CSS Manager")
    
    # Test tutti i framework
    for fw_name in FrameworkManager.list_frameworks():
        print(f"\n📦 Framework: {fw_name.upper()}")
        fw = FrameworkManager.get_framework(fw_name)
        
        print(f"  Container: {fw.CONTAINER}")
        print(f"  Button Primary: {fw.BTN_PRIMARY}")
        print(f"  Card: {fw.CARD}")
        print(f"  Alert Success: {fw.get_alert_class('success')}")
        print(f"  Badge Primary: {fw.get_badge_class('primary', pill=True)}")
