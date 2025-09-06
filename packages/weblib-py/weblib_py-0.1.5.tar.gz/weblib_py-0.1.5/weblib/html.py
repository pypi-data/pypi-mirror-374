"""
Modulo per la gestione degli elementi HTML
"""

from typing import List, Dict, Any, Union, Optional


class HtmlElement:
    """Classe base per tutti gli elementi HTML"""
    # html.py — HtmlElement.__init__
    def __init__(self, tag: str, content=None, classes=None, **attributes):
        self.tag = tag
        # ✅ normalizza sempre le classi
        if isinstance(classes, str):
            classes = classes.split()
        self.classes = classes or []
        self.attributes = attributes

        # contenuto
        if isinstance(content, str):
            self.content = content
        elif content is None:
            self.content = []
        else:
            self.content = content if isinstance(content, list) else [content]


    
    def add_class(self, class_name: str) -> 'HtmlElement':
        """Aggiunge una classe CSS all'elemento"""
        if class_name not in self.classes:
            self.classes.append(class_name)
        return self
    
    def remove_class(self, class_name: str) -> 'HtmlElement':
        """Rimuove una classe CSS dall'elemento"""
        if class_name in self.classes:
            self.classes.remove(class_name)
        return self
    
    def set_attribute(self, name: str, value: Any) -> 'HtmlElement':
        """Imposta un attributo dell'elemento"""
        self.attributes[name] = value
        return self
    
    def add_child(self, child: Union['HtmlElement', str]) -> 'HtmlElement':
        """Aggiunge un elemento figlio"""
        if isinstance(self.content, str):
            # Se il content è già una stringa, lo convertiamo in lista
            self.content = [self.content]
        
        if isinstance(self.content, list):
            self.content.append(child)
        return self
    
    def render(self, indent: int = 0) -> str:
        """Renderizza l'elemento HTML come stringa"""
        indent_str = "  " * indent
        
        # Costruiamo gli attributi
        attrs = []
        
        # Aggiungiamo le classi se presenti
        if self.classes:
            attrs.append(f'class="{" ".join(self.classes)}"')
        
        # Aggiungiamo gli altri attributi
        for key, value in self.attributes.items():
            if key != 'class':  # Le classi le abbiamo già gestite
                attrs.append(f'{key}="{value}"')
        
        attr_str = f' {" ".join(attrs)}' if attrs else ''
        
        # Tag auto-chiudenti (void elements)
        void_elements = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 
                        'link', 'meta', 'param', 'source', 'track', 'wbr'}
        
        if self.tag.lower() in void_elements:
            return f"{indent_str}<{self.tag}{attr_str} />"
        
        # Elemento con contenuto
        if isinstance(self.content, str):
            if '\n' in self.content:
                # Contenuto multiriga
                content_lines = self.content.split('\n')
                content_str = f"\n{indent_str}  " + f"\n{indent_str}  ".join(content_lines) + f"\n{indent_str}"
            else:
                # Contenuto su una riga
                content_str = self.content
                return f"{indent_str}<{self.tag}{attr_str}>{content_str}</{self.tag}>"
        
        elif isinstance(self.content, list) and self.content:
            child_strs = []
            for child in self.content:
                # ✅ se il figlio ha un metodo render() ed è *non* già un HtmlElement, chiamalo
                if hasattr(child, "render") and callable(getattr(child, "render")) \
                and not isinstance(child, HtmlElement):
                    rendered = child.render()
                    if isinstance(rendered, HtmlElement):
                        child_strs.append(rendered.render(indent + 1))
                    else:
                        child_strs.append(f"{indent_str}  {str(rendered)}")
                elif isinstance(child, HtmlElement):
                    child_strs.append(child.render(indent + 1))
                else:
                    child_strs.append(f"{indent_str}  {str(child)}")

            content_str = f"\n" + "\n".join(child_strs) + f"\n{indent_str}"
        else:
            # Nessun contenuto
            content_str = ""
            return f"{indent_str}<{self.tag}{attr_str}></{self.tag}>"
        
        return f"{indent_str}<{self.tag}{attr_str}>{content_str}</{self.tag}>"


# Elementi HTML specifici

class Html(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, **attributes):
        super().__init__('html', content, **attributes)


class Head(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, **attributes):
        super().__init__('head', content, **attributes)


class Body(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('body', content, classes, **attributes)


class Title(HtmlElement):
    def __init__(self, content: str = "", **attributes):
        super().__init__('title', content, **attributes)


class Meta(HtmlElement):
    def __init__(self, **attributes):
        # Rimuove 'content' dagli attributes se presente per evitare conflitti
        content = attributes.pop('content', None)
        super().__init__('meta', None, **attributes)
        # Se c'era un content, lo rimettiamo negli attributi
        if content is not None:
            self.attributes['content'] = content


class Link(HtmlElement):
    def __init__(self, **attributes):
        # Rimuove 'content' dagli attributes se presente per evitare conflitti
        content = attributes.pop('content', None)
        super().__init__('link', None, **attributes)
        # Se c'era un content, lo rimettiamo negli attributi
        if content is not None:
            self.attributes['content'] = content


class Script(HtmlElement):
    def __init__(self, content: str = "", **attributes):
        super().__init__('script', content, **attributes)


class Div(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('div', content, classes, **attributes)


class Span(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('span', content, classes, **attributes)


class P(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('p', content, classes, **attributes)


# Headers
class H1(HtmlElement):
    def __init__(self, content: str = "", classes: Optional[List[str]] = None, **attributes):
        super().__init__('h1', content, classes, **attributes)


class H2(HtmlElement):
    def __init__(self, content: str = "", classes: Optional[List[str]] = None, **attributes):
        super().__init__('h2', content, classes, **attributes)


class H3(HtmlElement):
    def __init__(self, content: str = "", classes: Optional[List[str]] = None, **attributes):
        super().__init__('h3', content, classes, **attributes)


class H4(HtmlElement):
    def __init__(self, content: str = "", classes: Optional[List[str]] = None, **attributes):
        super().__init__('h4', content, classes, **attributes)


class H5(HtmlElement):
    def __init__(self, content: str = "", classes: Optional[List[str]] = None, **attributes):
        super().__init__('h5', content, classes, **attributes)


class H6(HtmlElement):
    def __init__(self, content: str = "", classes: Optional[List[str]] = None, **attributes):
        super().__init__('h6', content, classes, **attributes)


class A(HtmlElement):
    def __init__(self, content: str = "", href: str = "#", 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('a', content, classes, href=href, **attributes)


class Img(HtmlElement):
    def __init__(self, src: str = "", alt: str = "", 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('img', None, classes, src=src, alt=alt, **attributes)


class Button(HtmlElement):
    def __init__(self, content: str = "", button_type: str = "button", 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('button', content, classes, type=button_type, **attributes)


class Input(HtmlElement):
    def __init__(self, input_type: str = "text", name: str = "", 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('input', None, classes, type=input_type, name=name, **attributes)


class Form(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 method: str = "POST", action: str = "", 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('form', content, classes, method=method, action=action, **attributes)


# Liste
class Ul(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('ul', content, classes, **attributes)


class Ol(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('ol', content, classes, **attributes)


class Li(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('li', content, classes, **attributes)


# Tabelle
class Table(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('table', content, classes, **attributes)


class Tr(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('tr', content, classes, **attributes)


class Td(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('td', content, classes, **attributes)


class Th(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('th', content, classes, **attributes)


# Elementi semantici HTML5
class Nav(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('nav', content, classes, **attributes)


class Header(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('header', content, classes, **attributes)


class Footer(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('footer', content, classes, **attributes)


class Section(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('section', content, classes, **attributes)


class Article(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('article', content, classes, **attributes)


class Aside(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('aside', content, classes, **attributes)


class Canvas(HtmlElement):
    def __init__(self, width: str = "300", height: str = "150", 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('canvas', None, classes, width=width, height=height, **attributes)


class Select(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('select', content, classes, **attributes)


class Option(HtmlElement):
    def __init__(self, content: str = "", value: str = "", 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('option', content, classes, value=value, **attributes)


class Label(HtmlElement):
    def __init__(self, content: str = "", for_: str = "", 
                 classes: Optional[List[str]] = None, **attributes):
        # 'for' è una parola chiave in Python, usiamo 'for_'
        if for_:
            attributes['for'] = for_
        super().__init__('label', content, classes, **attributes)


# Elementi aggiuntivi per il chatbot
class Style(HtmlElement):
    def __init__(self, content: str = "", **attributes):
        super().__init__('style', content, **attributes)


class I(HtmlElement):
    def __init__(self, content: Union[str, List['HtmlElement']] = "", 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('i', content, classes, **attributes)


class Hr(HtmlElement):
    def __init__(self, classes: Optional[List[str]] = None, **attributes):
        super().__init__('hr', None, classes, **attributes)
    
    def render(self) -> str:
        """Renderizza l'elemento hr (self-closing)"""
        attrs = []
        
        # Aggiungiamo le classi se presenti
        if self.classes:
            attrs.append(f'class="{" ".join(self.classes)}"')
        
        # Aggiungiamo altri attributi
        for key, value in self.attributes.items():
            if key != 'class':
                attrs.append(f'{key}="{value}"')
        
        attrs_str = ' ' + ' '.join(attrs) if attrs else ''
        return f'<{self.tag}{attrs_str} />'


class Textarea(HtmlElement):
    def __init__(self, content: str = "", rows: int = 3, cols: int = None,
                 classes: Optional[List[str]] = None, **attributes):
        if rows:
            attributes['rows'] = rows
        if cols:
            attributes['cols'] = cols
        super().__init__('textarea', content, classes, **attributes)


class Main(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('main', content, classes, **attributes)


class Thead(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('thead', content, classes, **attributes)


class Tbody(HtmlElement):
    def __init__(self, content: Union[str, List[HtmlElement], None] = None, 
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__('tbody', content, classes, **attributes)
