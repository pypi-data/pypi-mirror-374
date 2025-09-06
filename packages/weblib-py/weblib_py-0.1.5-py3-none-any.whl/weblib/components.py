"""
Sistema di Componenti per WebLib
Permette di creare componenti HTML riutilizzabili
"""
import uuid
from typing import Dict, Any, List, Optional, Callable
from .html import *
from .config import CSSClasses
from .utils import safe_int, safe_sub, safe_add

# Elementi HTML di base
def Strong(content, classes=None):
    """Elemento HTML strong"""
    return HtmlElement("strong", content, classes=classes)

def Small(content, classes=None):
    """Elemento HTML small"""
    return HtmlElement("small", content, classes=classes)

def Ol(items, classes=None):
    """Elemento HTML ordered list"""
    return HtmlElement("ol", items, classes=classes)

def H2(content, classes=None):
    """Elemento HTML h2"""
    return HtmlElement("h2", content, classes=classes)

def H3(content, classes=None):
    """Elemento HTML h3"""
    return HtmlElement("h3", content, classes=classes)

def H4(content, classes=None):
    """Elemento HTML h4"""
    return HtmlElement("h4", content, classes=classes)

def H5(content, classes=None):
    """Elemento HTML h5"""
    return HtmlElement("h5", content, classes=classes)

def Hr(classes=None):
    """Elemento HTML hr"""
    return HtmlElement("hr", "", classes=classes)


class Component:
    """Base class for reusable components with state management."""
    
    def __init__(self, **props):
        self.props = props
        self._children = []
        self.state = {}
        self.id = str(uuid.uuid4()) # Unique ID for each component instance

    def set_state(self, new_state: Dict[str, Any]):
        """
        Updates the component's state. In a live context, this would
        trigger a re-render and patch.
        """
        self.state.update(new_state)
        print(f"Component {self.id} state updated: {self.state}")

    def render(self) -> HtmlElement:
        """Must be implemented by subclasses."""
        raise NotImplementedError("Component must implement render() method")
    
    def add_child(self, child):
        """Aggiunge un figlio al componente"""
        self._children.append(child)
        return self
    
    def get_prop(self, key: str, default=None):
        """Ottiene una proprietà del componente"""
        return self.props.get(key, default)

class LiveComponent(Component):
    """
    A component that maintains a live connection with the browser
    for real-time updates.
    """
    def __init__(self, **props):
        super().__init__(**props)
        self.websocket = None

    async def mount(self, websocket):
        """Called when the component is first connected."""
        self.websocket = websocket
        await self.send_update()

    async def handle_event(self, event: Dict[str, Any]):
        """Handles incoming events from the browser."""
        event_type = event.get("type")
        handler_name = f"handle_{event_type}"
        if hasattr(self, handler_name):
            handler = getattr(self, handler_name)
            await handler(event.get("payload"))
            await self.send_update()

    async def send_update(self):
        """Renders the component and sends the HTML to the browser."""
        if self.websocket:
            html_content = self.render().render()
            await self.websocket.send_text(html_content)

    def render(self) -> HtmlElement:
        """
        Wraps the component's content with the necessary JavaScript bridge
        to establish the WebSocket connection.
        """
        component_content = self.render_content()
        
        # The client-side script to manage the WebSocket connection
        js_bridge = Script(f"""
            (() => {{
                const componentId = "{self.id}";
                const componentRoot = document.getElementById(componentId);
                if (componentRoot.dataset.weblibConnected) return; // Already connected
                componentRoot.dataset.weblibConnected = "true";

                const ws = new WebSocket("ws://" + window.location.host + "/ws");

                ws.onopen = () => {{
                    console.log(`WebSocket connected for component ${{componentId}}`);
                    ws.send(JSON.stringify({{ type: "mount", component_id: componentId }}));
                }};

                ws.onmessage = (event) => {{
                    const newHtml = event.data;
                    const currentElement = document.getElementById(componentId);
                    if (currentElement) {{
                        // Use morphdom to efficiently update the DOM
                        // For simplicity, we'll just replace the outerHTML for now
                        const newElement = new DOMParser().parseFromString(newHtml, "text/html").body.firstChild;
                        currentElement.parentNode.replaceChild(newElement, currentElement);
                    }}
                }};

                ws.onclose = () => {{
                    console.log("WebSocket disconnected.");
                }};

                componentRoot.addEventListener('click', e => {{
                    let target = e.target;
                    while (target && target !== componentRoot && !target.dataset.weblibEvent) {{
                        target = target.parentElement;
                    }}
                    if (target && target.dataset.weblibEvent) {{
                        e.preventDefault();
                        ws.send(JSON.stringify({{
                            type: "event",
                            component_id: componentId,
                            event: {{
                                type: target.dataset.weblibEvent,
                                payload: target.dataset.payload || {{}}
                            }}
                        }}));
                    }}
                }});
            }})();
        """)
        
        # Wrap the content in a div with the unique ID
        return Div([component_content, js_bridge], id=self.id)
        
    def render_content(self) -> HtmlElement:
        """Subclasses must implement this to define their actual content."""
        raise NotImplementedError("LiveComponent subclasses must implement render_content()")

class Card(Component):
    """Componente Card Bootstrap"""
    
    def render(self) -> HtmlElement:
        title = self.get_prop('title')
        text = self.get_prop('text')
        content_prop = self.get_prop('content', [])  # Aggiungi supporto per content
        footer = self.get_prop('footer')
        classes = self.get_prop('classes', [])
        
        card_classes = [CSSClasses.CARD] + classes
        
        content = []
        
        # Header se presente
        if self.get_prop('header'):
            header_div = Div(self.get_prop('header'), classes=[CSSClasses.CARD_HEADER])
            content.append(header_div)
        
        # Body
        body_content = []
        if title:
            if isinstance(title, str):
                body_content.append(H5(title, classes=[CSSClasses.CARD_TITLE]))
            else:
                body_content.append(title)
        
        if text:
            if isinstance(text, str):
                body_content.append(P(text, classes=[CSSClasses.CARD_TEXT]))
            else:
                body_content.append(text)
        
        # Aggiungi contenuto dal prop content
        if content_prop:
            if isinstance(content_prop, list):
                body_content.extend(content_prop)
            else:
                body_content.append(content_prop)
        
        # Aggiungi figli personalizzati
        body_content.extend(self._children)
        
        if body_content:
            content.append(Div(body_content, classes=[CSSClasses.CARD_BODY]))
        
        # Footer se presente
        if footer:
            footer_div = Div(footer, classes=[CSSClasses.CARD_FOOTER])
            content.append(footer_div)
        
        return Div(content, classes=card_classes)


class Alert(Component):
    """Componente Alert Bootstrap"""
    
    def render(self) -> HtmlElement:
        message = self.get_prop('message', '')
        alert_type = self.get_prop('type', 'info')  # info, success, warning, danger
        dismissible = self.get_prop('dismissible', False)
        classes = self.get_prop('classes', [])
        
        alert_classes = [CSSClasses.ALERT, f"alert-{alert_type}"] + classes
        
        content = [message] + self._children
        
        if dismissible:
            alert_classes.append('alert-dismissible')
            close_btn = Button([
                Span("&times;", **{"aria-hidden": "true"})
            ], classes=["btn-close"], **{"data-bs-dismiss": "alert", "aria-label": "Close"})
            content.append(close_btn)
        
        return Div(content, classes=alert_classes, role="alert")


class NavBar(Component):
    """Componente NavBar Bootstrap"""
    
    def render(self) -> HtmlElement:
        brand = self.get_prop('brand')
        links = self.get_prop('links', [])
        theme = self.get_prop('theme', 'light')  # light, dark
        expand = self.get_prop('expand', 'lg')
        classes = self.get_prop('classes', [])
        
        navbar_classes = [
            CSSClasses.NAVBAR,
            f"navbar-expand-{expand}",
            f"navbar-{theme}"
        ] + classes
        
        content = []
        
        # Brand
        if brand:
            if isinstance(brand, str):
                brand_element = A(brand, classes=[CSSClasses.NAVBAR_BRAND], href="/")
            else:
                brand_element = brand
            content.append(brand_element)
        
        # Links
        if links:
            nav_links = []
            for link in links:
                if isinstance(link, dict):
                    nav_links.append(
                        Li(A(link['text'], href=link['url'], classes=[CSSClasses.NAV_LINK]))
                    )
                else:
                    nav_links.append(Li(link))
            
            nav_ul = Ul(nav_links, classes=["navbar-nav", "me-auto"])
            content.append(nav_ul)
        
        # Figli personalizzati
        content.extend(self._children)
        
        return Nav(content, classes=navbar_classes)


class Modal(Component):
    """Componente Modal Bootstrap"""
    
    def render(self) -> HtmlElement:
        modal_id = self.get_prop('id', 'modal')
        title = self.get_prop('title', 'Modal')
        size = self.get_prop('size', '')  # '', 'sm', 'lg', 'xl'
        
        modal_classes = ["modal", "fade"]
        dialog_classes = ["modal-dialog"]
        
        if size:
            dialog_classes.append(f"modal-{size}")
        
        # Header
        header = Div([
            H5(title, classes=["modal-title"]),
            Button([Span("&times;")], classes=["btn-close"], **{"data-bs-dismiss": "modal"})
        ], classes=["modal-header"])
        
        # Body
        body = Div(self._children, classes=["modal-body"])
        
        # Footer (se specificato)
        footer_content = self.get_prop('footer')
        content = [header, body]
        
        if footer_content:
            footer = Div(footer_content, classes=["modal-footer"])
            content.append(footer)
        
        modal_content = Div(content, classes=["modal-content"])
        modal_dialog = Div([modal_content], classes=dialog_classes)
        
        return Div([modal_dialog], 
                  classes=modal_classes, 
                  id=modal_id, 
                  tabindex="-1",
                  **{"aria-hidden": "true"})


class Breadcrumb(Component):
    """Componente Breadcrumb Bootstrap"""
    
    def render(self) -> HtmlElement:
        items = self.get_prop('items', [])
        
        breadcrumb_items = []
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            
            if isinstance(item, dict):
                text = item['text']
                url = item.get('url')
                
                if is_last or not url:
                    # Ultimo elemento o senza link
                    breadcrumb_items.append(Li(text, classes=["breadcrumb-item", "active"]))
                else:
                    # Elemento con link
                    breadcrumb_items.append(Li(A(text, href=url), classes=["breadcrumb-item"]))
            else:
                # Stringa semplice
                classes = ["breadcrumb-item"]
                if is_last:
                    classes.append("active")
                breadcrumb_items.append(Li(item, classes=classes))
        
        return Nav([
            Ul(breadcrumb_items, classes=["breadcrumb"])
        ], **{"aria-label": "breadcrumb"})


class Pagination(Component):
    """Componente Paginazione Bootstrap (safe)"""
    
    def render(self) -> HtmlElement:
        from .utils import safe_int  # assicurati che esista e gestisca spazi/segni
        
        # 1) Coercizione robusta a int
        current_page = safe_int(self.get_prop('current_page', 1), default=1)
        total_pages = safe_int(self.get_prop('total_pages', 1), default=1)
        
        # 2) Guard-rails
        if current_page < 1:
            current_page = 1
        if total_pages < 1:
            total_pages = 1
        if current_page > total_pages:
            current_page = total_pages
        
        base_url = self.get_prop('base_url', '?page=')
        pages = []
        
        # Prev
        if current_page > 1:
            prev_page = current_page - 1
            pages.append(Li(A("Previous", href=f"{base_url}{prev_page}"), classes=["page-item"]))
        else:
            pages.append(Li(Span("Previous"), classes=["page-item", "disabled"]))
        
        # Finestre di pagine (start/end) in modo sicuro
        start = max(1, current_page - 2)
        end = min(total_pages, current_page + 2)
        
        # Normalizza perché range è esclusivo sul limite superiore
        for page in range(start, end + 1):
            if page == current_page:
                pages.append(Li(Span(str(page)), classes=["page-item", "active"]))
            else:
                pages.append(Li(A(str(page), href=f"{base_url}{page}"), classes=["page-item"]))
        
        # Next
        if current_page < total_pages:
            next_page = current_page + 1
            pages.append(Li(A("Next", href=f"{base_url}{next_page}"), classes=["page-item"]))
        else:
            pages.append(Li(Span("Next"), classes=["page-item", "disabled"]))
        
        return Nav([Ul(pages, classes=["pagination"])])


class Badge(Component):
    """Componente Badge Bootstrap"""
    
    def render(self) -> HtmlElement:
        text = self.get_prop('text', '')
        variant = self.get_prop('variant', 'primary')
        pill = self.get_prop('pill', False)
        classes = self.get_prop('classes', [])
        
        badge_classes = [f"badge", f"bg-{variant}"] + classes
        if pill:
            badge_classes.append("rounded-pill")
        
        return Span([text] + self._children, classes=badge_classes)


# Decorator per registrare componenti
_registered_components = {}

def component(name: str = None):
    """Decorator per registrare un componente personalizzato"""
    def decorator(cls):
        component_name = name or cls.__name__.lower()
        _registered_components[component_name] = cls
        return cls
    return decorator


def get_component(name: str) -> Optional[type]:
    """Ottiene un componente registrato"""
    return _registered_components.get(name)


def list_components() -> List[str]:
    """Lista tutti i componenti registrati"""
    return list(_registered_components.keys())


class Carousel(Component):
    """Componente Carousel Bootstrap"""
    
    def render(self) -> HtmlElement:
        items = self.get_prop('items', [])
        carousel_id = self.get_prop('id', 'carousel')
        interval = self.get_prop('interval', 5000)
        controls = self.get_prop('controls', True)
        indicators = self.get_prop('indicators', True)
        classes = self.get_prop('classes', [])
        
        carousel_classes = ["carousel", "slide"] + classes
        
        content = []
        
        # Indicators
        if indicators:
            indicator_buttons = []
            for i in range(len(items)):
                indicator_buttons.append(
                    Button("", attrs={
                        "type": "button",
                        "data-bs-target": f"#{carousel_id}",
                        "data-bs-slide-to": str(i),
                        "aria-label": f"Slide {i+1}",
                        "aria-current": "true" if i == 0 else "false"
                    }, classes=["active"] if i == 0 else [])
                )
            content.append(Div(indicator_buttons, classes=["carousel-indicators"]))
        
        # Items
        carousel_items = []
        for i, item in enumerate(items):
            item_content = []
            
            # Image
            if 'src' in item:
                item_content.append(
                    Img(src=item['src'], 
                        classes=["d-block", "w-100"],
                        attrs={"alt": item.get('alt', '')})
                )
            
            # Caption
            if 'caption_title' in item or 'caption_text' in item:
                caption = []
                if 'caption_title' in item:
                    caption.append(H5(item['caption_title']))
                if 'caption_text' in item:
                    caption.append(P(item['caption_text']))
                item_content.append(
                    Div(caption, classes=["carousel-caption", "d-none", "d-md-block"])
                )
            
            carousel_items.append(
                Div(item_content, 
                    classes=["carousel-item"] + (["active"] if i == 0 else []))
            )
        
        content.append(Div(carousel_items, classes=["carousel-inner"]))
        
        # Controls
        if controls:
            content.extend([
                Button([
                    Span("Previous", classes=["visually-hidden"]),
                    Span("", classes=["carousel-control-prev-icon"])
                ], classes=["carousel-control-prev"],
                   attrs={
                       "type": "button",
                       "data-bs-target": f"#{carousel_id}",
                       "data-bs-slide": "prev"
                   }),
                Button([
                    Span("Next", classes=["visually-hidden"]),
                    Span("", classes=["carousel-control-next-icon"])
                ], classes=["carousel-control-next"],
                   attrs={
                       "type": "button",
                       "data-bs-target": f"#{carousel_id}",
                       "data-bs-slide": "next"
                   })
            ])
        
        return Div(content, 
                  classes=carousel_classes,
                  attrs={
                      "id": carousel_id,
                      "data-bs-ride": "carousel",
                      "data-bs-interval": str(interval)
                  })


class Progress(Component):
    """Componente Progress Bar Bootstrap"""
    
    def render(self) -> HtmlElement:
        value = self.get_prop('value', 0)
        max_value = self.get_prop('max', 100)
        label = self.get_prop('label', '')
        height = self.get_prop('height')
        striped = self.get_prop('striped', False)
        animated = self.get_prop('animated', False)
        variant = self.get_prop('variant', 'primary')
        classes = self.get_prop('classes', [])
        
        bar_classes = [f"progress-bar", f"bg-{variant}"]
        if striped:
            bar_classes.append("progress-bar-striped")
        if animated:
            bar_classes.append("progress-bar-animated")
        
        progress_attrs = {}
        if height:
            progress_attrs["style"] = f"height: {height}px"
        
        progress_bar = Div(
            label,
            classes=bar_classes,
            attrs={
                "role": "progressbar",
                "style": f"width: {value}%",
                "aria-valuenow": str(value),
                "aria-valuemin": "0",
                "aria-valuemax": str(max_value)
            }
        )
        
        return Div([progress_bar], 
                  classes=["progress"] + classes,
                  attrs=progress_attrs)


class Accordion(Component):
    """Componente Accordion Bootstrap"""
    
    def render(self) -> HtmlElement:
        items = self.get_prop('items', [])
        accordion_id = self.get_prop('id', 'accordion')
        flush = self.get_prop('flush', False)
        always_open = self.get_prop('always_open', False)
        classes = self.get_prop('classes', [])
        
        accordion_classes = ["accordion"]
        if flush:
            accordion_classes.append("accordion-flush")
        accordion_classes.extend(classes)
        
        accordion_items = []
        for i, item in enumerate(items):
            header = H2(
                Button(
                    item['title'],
                    classes=["accordion-button"] + (["collapsed"] if i > 0 else []),
                    attrs={
                        "type": "button",
                        "data-bs-toggle": "collapse",
                        "data-bs-target": f"#{accordion_id}-collapse-{i}",
                        "aria-expanded": "true" if i == 0 else "false",
                        "aria-controls": f"{accordion_id}-collapse-{i}"
                    }
                ),
                classes=["accordion-header"]
            )
            
            body = Div([
                Div(item['content'], classes=["accordion-body"])
            ], classes=["accordion-collapse", "collapse"] + (["show"] if i == 0 else []),
               attrs={
                   "id": f"{accordion_id}-collapse-{i}",
                   "data-bs-parent": "" if always_open else f"#{accordion_id}"
               })
            
            accordion_items.append(
                Div([header, body], classes=["accordion-item"])
            )
        
        return Div(accordion_items, 
                  classes=accordion_classes,
                  attrs={"id": accordion_id})


class Toast(Component):
    """Componente Toast Bootstrap per notifiche"""
    
    def render(self) -> HtmlElement:
        title = self.get_prop('title', '')
        message = self.get_prop('message', '')
        autohide = self.get_prop('autohide', True)
        delay = self.get_prop('delay', 5000)
        position = self.get_prop('position', 'bottom-end')  # top-start, top-end, bottom-start, bottom-end
        classes = self.get_prop('classes', [])
        
        position_classes = {
            'top-start': ['top-0', 'start-0'],
            'top-end': ['top-0', 'end-0'],
            'bottom-start': ['bottom-0', 'start-0'],
            'bottom-end': ['bottom-0', 'end-0']
        }
        
        toast = Div([
            # Header
            Div([
                Strong(title, classes=["me-auto"]),
                Button(
                    Span("", classes=["btn-close"]),
                    attrs={
                        "data-bs-dismiss": "toast",
                        "aria-label": "Close"
                    }
                )
            ], classes=["toast-header"]),
            # Body
            Div(message, classes=["toast-body"])
        ], classes=["toast"] + classes,
           attrs={
               "role": "alert",
               "aria-live": "assertive",
               "aria-atomic": "true",
               "data-bs-autohide": str(autohide).lower(),
               "data-bs-delay": str(delay)
           })
        
        return Div([toast], 
                  classes=["toast-container", "position-fixed", "p-3"] + 
                         position_classes.get(position, []))


class ListGroup(Component):
    """Componente List Group Bootstrap"""
    
    def render(self) -> HtmlElement:
        items = self.get_prop('items', [])
        flush = self.get_prop('flush', False)
        numbered = self.get_prop('numbered', False)
        horizontal = self.get_prop('horizontal', False)
        classes = self.get_prop('classes', [])
        
        list_classes = ["list-group"] + classes
        if flush:
            list_classes.append("list-group-flush")
        if horizontal:
            list_classes.append("list-group-horizontal")
        
        list_items = []
        for item in items:
            if isinstance(item, dict):
                item_classes = ["list-group-item"]
                if item.get('active'):
                    item_classes.append("active")
                if item.get('disabled'):
                    item_classes.append("disabled")
                if 'variant' in item:
                    item_classes.append(f"list-group-item-{item['variant']}")
                
                if 'href' in item:
                    list_items.append(
                        A(item['content'], 
                          href=item['href'],
                          classes=item_classes + ["list-group-item-action"])
                    )
                else:
                    list_items.append(
                        Li(item['content'], classes=item_classes)
                    )
            else:
                list_items.append(
                    Li(item, classes=["list-group-item"])
                )
        
        return (Ol if numbered else Ul)(list_items, classes=list_classes)



class ButtonGroup(Component):
    """Componente Button Group Bootstrap"""
    
    def render(self) -> HtmlElement:
        buttons = self.get_prop('buttons', [])
        vertical = self.get_prop('vertical', False)
        size = self.get_prop('size', '')  # sm, lg
        classes = self.get_prop('classes', [])
        
        group_classes = ["btn-group"]
        if vertical:
            group_classes = ["btn-group-vertical"]
        if size:
            group_classes.append(f"btn-group-{size}")
        group_classes.extend(classes)
        
        return Div(buttons, 
                  classes=group_classes,
                  attrs={"role": "group"})


class Dropdown(Component):
    """Componente Dropdown Bootstrap (token CSS corretti)"""
    
    def render(self) -> HtmlElement:
        items = self.get_prop('items', [])
        label = self.get_prop('label', 'Dropdown')
        split = self.get_prop('split', False)
        direction = self.get_prop('direction', 'down')  # down, up, start, end
        dark = self.get_prop('dark', False)
        variant = self.get_prop('variant', 'primary')
        size = self.get_prop('size', '')
        classes = self.get_prop('classes', [])
        
        # Correzione: token separati, non una singola stringa con spazio
        btn_classes = ["btn", f"btn-{variant}"]
        if size:
            btn_classes.append(f"btn-{size}")
        
        dropdown_classes = ["dropdown"]
        if direction != 'down':
            dropdown_classes.append(f"drop{direction}")
        dropdown_classes.extend(classes)
        
        menu_classes = ["dropdown-menu"]
        if dark:
            menu_classes.append("dropdown-menu-dark")
        
        menu_items = []
        for item in items:
            if item == "divider":
                menu_items.append(Hr(classes=["dropdown-divider"]))
            elif isinstance(item, dict):
                if item.get('header'):
                    menu_items.append(H6(item['header'], classes=["dropdown-header"]))
                else:
                    menu_items.append(
                        A(
                            item['text'],
                            href=item.get('href', '#'),
                            classes=["dropdown-item"] + (['active'] if item.get('active') else []) + (['disabled'] if item.get('disabled') else [])
                        )
                    )
        
        if split:
            button_content = [
                Button(label, classes=btn_classes),
                Button(
                    Span("Toggle Dropdown", classes=["visually-hidden"]),
                    classes=btn_classes + ["dropdown-toggle", "dropdown-toggle-split"],
                    attrs={"data-bs-toggle": "dropdown", "aria-expanded": "false"}
                )
            ]
        else:
            button_content = [
                Button(
                    [label, Span("", classes=["ms-1"]), ""],
                    classes=btn_classes + ["dropdown-toggle"],
                    attrs={"data-bs-toggle": "dropdown", "aria-expanded": "false"}
                )
            ]
        
        button_content.append(Ul(menu_items, classes=menu_classes))
        return Div(button_content, classes=dropdown_classes)


class NavTabs(Component):
    """Componente Nav Tabs/Pills Bootstrap"""
    
    def render(self) -> HtmlElement:
        items = self.get_prop('items', [])
        pills = self.get_prop('pills', False)
        fill = self.get_prop('fill', False)
        justified = self.get_prop('justified', False)
        vertical = self.get_prop('vertical', False)
        classes = self.get_prop('classes', [])
        
        nav_classes = ["nav"]
        if pills:
            nav_classes.append("nav-pills")
        else:
            nav_classes.append("nav-tabs")
        if fill:
            nav_classes.append("nav-fill")
        if justified:
            nav_classes.append("nav-justified")
        if vertical:
            nav_classes.append("flex-column")
        nav_classes.extend(classes)
        
        nav_items = []
        for item in items:
            item_content = A(
                item['text'],
                href=item.get('href', '#'),
                classes=["nav-link"] + 
                       (["active"] if item.get('active') else []) +
                       (["disabled"] if item.get('disabled') else [])
            )
            nav_items.append(Li(item_content, classes=["nav-item"]))
        
        return Ul(nav_items, classes=nav_classes)


class Offcanvas(Component):
    """Componente Offcanvas Bootstrap"""
    
    def render(self) -> HtmlElement:
        title = self.get_prop('title', '')
        content = self.get_prop('content', [])
        placement = self.get_prop('placement', 'start')  # start, end, top, bottom
        backdrop = self.get_prop('backdrop', True)
        scroll = self.get_prop('scroll', False)
        classes = self.get_prop('classes', [])
        
        offcanvas_classes = ["offcanvas", f"offcanvas-{placement}"]
        offcanvas_classes.extend(classes)
        
        return Div([
            Div([
                H5(title, classes=["offcanvas-title"]),
                Button(
                    Span("", classes=["btn-close"]),
                    attrs={
                        "data-bs-dismiss": "offcanvas",
                        "aria-label": "Close"
                    }
                )
            ], classes=["offcanvas-header"]),
            Div(content, classes=["offcanvas-body"])
        ], classes=offcanvas_classes,
           attrs={
               "tabindex": "-1",
               "data-bs-backdrop": str(backdrop).lower(),
               "data-bs-scroll": str(scroll).lower()
           })


class Placeholder(Component):
    """Componente Placeholder Bootstrap"""
    
    def render(self) -> HtmlElement:
        width = self.get_prop('width', '100%')
        size = self.get_prop('size', '')  # xs, sm, lg
        animation = self.get_prop('animation', 'glow')  # glow, wave
        variant = self.get_prop('variant', '')  # primary, secondary, etc.
        classes = self.get_prop('classes', [])
        
        placeholder_classes = ["placeholder"]
        if animation:
            placeholder_classes.append(f"placeholder-{animation}")
        if size:
            placeholder_classes.append(f"placeholder-{size}")
        if variant:
            placeholder_classes.append(f"bg-{variant}")
        placeholder_classes.extend(classes)
        
        return Span(
            "",
            classes=placeholder_classes,
            attrs={"style": f"width: {width}"}
        )


class Popover(Component):
    """Componente Popover Bootstrap"""
    
    def render(self) -> HtmlElement:
        trigger = self.get_prop('trigger', '')
        title = self.get_prop('title', '')
        content = self.get_prop('content', '')
        placement = self.get_prop('placement', 'top')  # top, bottom, left, right
        html = self.get_prop('html', False)
        classes = self.get_prop('classes', [])
        
        return Button(
            trigger,
            classes=["btn", "btn-secondary"] + classes,
            attrs={
                "data-bs-toggle": "popover",
                "data-bs-placement": placement,
                "data-bs-title": title,
                "data-bs-content": content,
                "data-bs-html": str(html).lower()
            }
        )


class Spinner(Component):
    """Componente Spinner Bootstrap"""
    
    def render(self) -> HtmlElement:
        type = self.get_prop('type', 'border')  # border, grow
        size = self.get_prop('size', '')  # sm
        variant = self.get_prop('variant', 'primary')
        classes = self.get_prop('classes', [])
        
        spinner_classes = [f"spinner-{type}"]
        if size:
            spinner_classes.append(f"spinner-{type}-{size}")
        if variant:
            spinner_classes.append(f"text-{variant}")
        spinner_classes.extend(classes)
        
        return Div(
            Span("Loading...", classes=["visually-hidden"]),
            classes=spinner_classes,
            attrs={"role": "status"}
        )


class Tooltip(Component):
    """Componente Tooltip Bootstrap"""
    
    def render(self) -> HtmlElement:
        trigger = self.get_prop('trigger', '')
        title = self.get_prop('title', '')
        placement = self.get_prop('placement', 'top')  # top, bottom, left, right
        html = self.get_prop('html', False)
        classes = self.get_prop('classes', [])
        
        return Button(
            trigger,
            classes=["btn", "btn-secondary"] + classes,
            attrs={
                "data-bs-toggle": "tooltip",
                "data-bs-placement": placement,
                "data-bs-title": title,
                "data-bs-html": str(html).lower()
            }
        )


class ScrollSpy(Component):
    """Componente ScrollSpy Bootstrap"""
    
    def render(self) -> HtmlElement:
        target = self.get_prop('target', '')
        offset = self.get_prop('offset', 0)
        method = self.get_prop('method', 'auto')  # auto, position, offset
        content = self.get_prop('content', [])
        classes = self.get_prop('classes', [])
        
        return Div(
            content,
            classes=classes,
            attrs={
                "data-bs-spy": "scroll",
                "data-bs-target": target,
                "data-bs-offset": str(offset),
                "data-bs-method": method,
                "tabindex": "0"
            }
        )


class Collapse(Component):
    """Componente Collapse Bootstrap"""
    
    def render(self) -> HtmlElement:
        id = self.get_prop('id', '')
        trigger = self.get_prop('trigger', '')
        content = self.get_prop('content', [])
        horizontal = self.get_prop('horizontal', False)
        classes = self.get_prop('classes', [])
        
        trigger_button = Button(
            trigger,
            classes=["btn", "btn-primary"],
            attrs={
                "data-bs-toggle": "collapse",
                "data-bs-target": f"#{id}",
                "aria-expanded": "false",
                "aria-controls": id
            }
        )
        
        collapse_classes = ["collapse"]
        if horizontal:
            collapse_classes.append("collapse-horizontal")
        collapse_classes.extend(classes)
        
        collapse_content = Div(
            content,
            classes=collapse_classes,
            attrs={"id": id}
        )
        
        return Div([trigger_button, collapse_content])


class CodeSnippet(Component):
    """Componente per visualizzare snippet di codice con syntax highlighting.
    
    Utilizza Prism.js per l'evidenziazione della sintassi e supporta numerosi linguaggi.
    Include features come:
    - Numerazione delle righe
    - Copia negli appunti
    - Evidenziazione di righe specifiche
    - Tema personalizzabile
    - Linguaggi multipli
    """
    
    # Mapping dei linguaggi comuni ai loro alias Prism
    LANGUAGE_ALIASES = {
        'python': 'python',
        'py': 'python',
        'javascript': 'javascript',
        'js': 'javascript',
        'typescript': 'typescript',
        'ts': 'typescript',
        'html': 'html',
        'css': 'css',
        'json': 'json',
        'yaml': 'yaml',
        'yml': 'yaml',
        'bash': 'bash',
        'shell': 'shell-session',
        'sql': 'sql',
        'php': 'php',
        'java': 'java',
        'cpp': 'cpp',
        'c++': 'cpp',
        'c': 'c',
        'csharp': 'csharp',
        'cs': 'csharp',
        'ruby': 'ruby',
        'rb': 'ruby',
        'go': 'go',
        'rust': 'rust',
        'swift': 'swift',
        'kotlin': 'kotlin',
        'markdown': 'markdown',
        'md': 'markdown',
        'xml': 'xml',
        'dockerfile': 'dockerfile',
        'docker': 'dockerfile',
        'graphql': 'graphql',
        'regex': 'regex',
    }
    
    def render(self) -> HtmlElement:
        code = self.get_prop('code', '')
        language = self.get_prop('language', 'text')
        show_line_numbers = self.get_prop('show_line_numbers', True)
        highlight_lines = self.get_prop('highlight_lines', [])
        theme = self.get_prop('theme', 'default')  # default, dark, okaidia, twilight, etc.
        max_height = self.get_prop('max_height', None)
        copy_button = self.get_prop('copy_button', True)
        classes = self.get_prop('classes', [])
        
        # Normalizza il linguaggio
        language = self.LANGUAGE_ALIASES.get(language.lower(), 'text')
        
        # Prepara le classi CSS
        pre_classes = ["language-" + language]
        if show_line_numbers:
            pre_classes.append("line-numbers")
        pre_classes.extend(classes)
        
        # Prepara gli stili
        styles = {}
        if max_height:
            styles["max-height"] = f"{max_height}px"
            styles["overflow-y"] = "auto"
        
        # Gestisce l'evidenziazione delle righe
        if highlight_lines:
            highlight_attr = {"data-line": ",".join(map(str, highlight_lines))}
        else:
            highlight_attr = {}
        
        # Formatta il codice (rimuove indentazione comune)
        if isinstance(code, str):
            code = code.strip()
        
        # Crea il pre e code elements
        code_element = Div(
            code,
            tag="code",
            classes=["language-" + language]
        )
        
        pre_element = Div(
            code_element,
            tag="pre",
            classes=pre_classes,
            attrs={
                "style": "; ".join(f"{k}: {v}" for k, v in styles.items()),
                **highlight_attr
            }
        )
        
        # Aggiunge il pulsante di copia se richiesto
        if copy_button:
            copy_btn = Button(
                Span("Copy", classes=["copy-text"]),
                classes=["copy-button"],
                attrs={
                    "data-clipboard-target": f"#{pre_element.id}",
                    "title": "Copy to clipboard"
                }
            )
            
            # Aggiungi CSS per il pulsante di copia
            copy_button_css = """
            <style>
                .code-wrapper {
                    position: relative;
                }
                .copy-button {
                    position: absolute;
                    right: 10px;
                    top: 10px;
                    padding: 8px 12px;
                    background: rgba(255, 255, 255, 0.1);
                    border: none;
                    border-radius: 4px;
                    color: #fff;
                    cursor: pointer;
                    opacity: 0;
                    transition: opacity 0.3s;
                }
                .code-wrapper:hover .copy-button {
                    opacity: 1;
                }
                .copy-button:hover {
                    background: rgba(255, 255, 255, 0.2);
                }
            </style>
            """
            
            return Div([
                Div(copy_button_css, raw=True),
                Div([pre_element, copy_btn], classes=["code-wrapper"])
            ])
        
        return pre_element


# Registra i componenti predefiniti
_registered_components.update({
    'card': Card,
    'alert': Alert,
    'navbar': NavBar,
    'modal': Modal,
    'breadcrumb': Breadcrumb,
    'pagination': Pagination,
    'badge': Badge,
    'carousel': Carousel,
    'progress': Progress,
    'accordion': Accordion,
    'toast': Toast,
    'listgroup': ListGroup,
    'buttongroup': ButtonGroup,
    'dropdown': Dropdown,
    'navtabs': NavTabs,
    'offcanvas': Offcanvas,
    'placeholder': Placeholder,
    'popover': Popover,
    'spinner': Spinner,
    'tooltip': Tooltip,
    'scrollspy': ScrollSpy,
    'collapse': Collapse,
    'codesnippet': CodeSnippet,
})