"""
Modulo per l'integrazione di grafici in WebLib
Supporta Chart.js, Plotly.js e altre librerie di charting
"""

from typing import Dict, List, Any, Optional, Union
from .html import HtmlElement, Div, Script


class ChartBase(HtmlElement):
    """Classe base per tutti i tipi di grafici"""
    
    def __init__(self, chart_id: str, width: str = "100%", height: str = "400px",
                 classes: Optional[List[str]] = None, **attributes):
        self.chart_id = chart_id
        self.width = width
        self.height = height
        self.chart_data = {}
        self.chart_options = {}
        
        # Crea un div container per il grafico
        super().__init__('div', None, classes, id=chart_id, 
                        style=f"width: {width}; height: {height};", **attributes)
    
    def set_data(self, data: Dict[str, Any]) -> 'ChartBase':
        """Imposta i dati del grafico"""
        self.chart_data = data
        return self
    
    def set_options(self, options: Dict[str, Any]) -> 'ChartBase':
        """Imposta le opzioni del grafico"""
        self.chart_options = options
        return self
    
    def get_init_script(self) -> str:
        """Restituisce lo script JavaScript per inizializzare il grafico"""
        return ""


class ChartJS(ChartBase):
    """Classe per grafici Chart.js"""
    
    CDN_URL = "https://cdn.jsdelivr.net/npm/chart.js"
    
    def __init__(self, chart_id: str, chart_type: str = "line", 
                 width: str = "100%", height: str = "400px",
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__(chart_id, width, height, classes, **attributes)
        self.chart_type = chart_type
        # Chart.js ha bisogno di un canvas, non div
        self.tag = "canvas"
    
    def line_chart(self, labels: List[str], datasets: List[Dict[str, Any]]) -> 'ChartJS':
        """Crea un grafico a linee"""
        self.chart_type = "line"
        self.chart_data = {
            "labels": labels,
            "datasets": datasets
        }
        return self
    
    def bar_chart(self, labels: List[str], datasets: List[Dict[str, Any]]) -> 'ChartJS':
        """Crea un grafico a barre"""
        self.chart_type = "bar"
        self.chart_data = {
            "labels": labels,
            "datasets": datasets
        }
        return self
    
    def pie_chart(self, labels: List[str], data: List[float], 
                  background_colors: Optional[List[str]] = None) -> 'ChartJS':
        """Crea un grafico a torta"""
        self.chart_type = "pie"
        
        colors = background_colors or [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
        ]
        
        self.chart_data = {
            "labels": labels,
            "datasets": [{
                "data": data,
                "backgroundColor": colors[:len(data)],
                "borderWidth": 1
            }]
        }
        return self
    
    def get_init_script(self) -> str:
        """Genera lo script JavaScript per Chart.js"""
        import json
        
        chart_config = {
            "type": self.chart_type,
            "data": self.chart_data,
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                **self.chart_options
            }
        }
        
        # Serializza la configurazione in modo sicuro
        config_json = json.dumps(chart_config, indent=2)
        
        return f"""
document.addEventListener('DOMContentLoaded', function() {{
    const canvas = document.getElementById('{self.chart_id}');
    if (canvas) {{
        const ctx = canvas.getContext('2d');
        new Chart(ctx, {config_json});
    }} else {{
        console.error('Canvas element with id "{self.chart_id}" not found');
    }}
}});
"""


class PlotlyJS(ChartBase):
    """Classe per grafici Plotly.js"""
    
    CDN_URL = "https://cdn.plot.ly/plotly-latest.min.js"
    
    def __init__(self, chart_id: str, width: str = "100%", height: str = "400px",
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__(chart_id, width, height, classes, **attributes)
        self.traces = []
        self.layout = {}
    
    def add_trace(self, trace: Dict[str, Any]) -> 'PlotlyJS':
        """Aggiunge una traccia al grafico"""
        self.traces.append(trace)
        return self
    
    def scatter_plot(self, x: List[Any], y: List[Any], name: str = "", 
                    mode: str = "markers") -> 'PlotlyJS':
        """Crea un grafico a dispersione"""
        trace = {
            "x": x,
            "y": y,
            "type": "scatter",
            "mode": mode,
            "name": name
        }
        return self.add_trace(trace)
    
    def line_plot(self, x: List[Any], y: List[Any], name: str = "") -> 'PlotlyJS':
        """Crea un grafico a linee"""
        return self.scatter_plot(x, y, name, "lines+markers")
    
    def bar_plot(self, x: List[Any], y: List[Any], name: str = "") -> 'PlotlyJS':
        """Crea un grafico a barre"""
        trace = {
            "x": x,
            "y": y,
            "type": "bar",
            "name": name
        }
        return self.add_trace(trace)
    
    def set_layout(self, layout: Dict[str, Any]) -> 'PlotlyJS':
        """Imposta il layout del grafico"""
        self.layout = layout
        return self
    
    def get_init_script(self) -> str:
        """Genera lo script JavaScript per Plotly.js"""
        import json
        
        return f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            Plotly.newPlot('{self.chart_id}', {json.dumps(self.traces)}, {json.dumps(self.layout)});
        }});
        </script>
        """


class ApexCharts(ChartBase):
    """Classe per grafici ApexCharts"""
    
    CDN_URL = "https://cdn.jsdelivr.net/npm/apexcharts"
    
    def __init__(self, chart_id: str, width: str = "100%", height: str = "400px",
                 classes: Optional[List[str]] = None, **attributes):
        super().__init__(chart_id, width, height, classes, **attributes)
        self.chart_config = {
            "chart": {
                "type": "line",
                "height": height,
                "width": width
            },
            "series": [],
            "xaxis": {},
            "yaxis": {}
        }
    
    def line_chart(self, series: List[Dict[str, Any]], categories: Optional[List[str]] = None) -> 'ApexCharts':
        """Crea un grafico a linee"""
        self.chart_config.update({
            "chart": {"type": "line", "height": self.height, "width": self.width},
            "series": series,
            "xaxis": {"categories": categories} if categories else {}
        })
        return self
    
    def area_chart(self, series: List[Dict[str, Any]], categories: Optional[List[str]] = None) -> 'ApexCharts':
        """Crea un grafico ad area"""
        self.chart_config.update({
            "chart": {"type": "area", "height": self.height, "width": self.width},
            "series": series,
            "xaxis": {"categories": categories} if categories else {}
        })
        return self
    
    def get_init_script(self) -> str:
        """Genera lo script JavaScript per ApexCharts"""
        import json
        
        return f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const options = {json.dumps(self.chart_config)};
            const chart = new ApexCharts(document.querySelector('#{self.chart_id}'), options);
            chart.render();
        }});
        </script>
        """


class ChartBuilder:
    """Builder per creare facilmente grafici con WebLib"""
    
    @staticmethod
    def create_chartjs_page(title: str = "Chart.js Dashboard") -> 'ChartPage':
        """Crea una pagina con supporto Chart.js"""
        return ChartPage(title, ChartJS.CDN_URL, "chartjs")
    
    @staticmethod
    def create_plotly_page(title: str = "Plotly Dashboard") -> 'ChartPage':
        """Crea una pagina con supporto Plotly.js"""
        return ChartPage(title, PlotlyJS.CDN_URL, "plotly")
    
    @staticmethod
    def create_apex_page(title: str = "ApexCharts Dashboard") -> 'ChartPage':
        """Crea una pagina con supporto ApexCharts"""
        return ChartPage(title, ApexCharts.CDN_URL, "apex")


class ChartPage:
    """Helper per creare pagine con grafici"""
    
    def __init__(self, title: str, chart_library_url: str, chart_type: str):
        self.title = title
        self.chart_library_url = chart_library_url
        self.chart_type = chart_type
        self.charts = []
        self.css_links = [
            "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
        ]
        self.js_links = [chart_library_url]
    
    def add_chart(self, chart: ChartBase) -> 'ChartPage':
        """Aggiunge un grafico alla pagina"""
        self.charts.append(chart)
        return self
    
    def add_css(self, href: str) -> 'ChartPage':
        """Aggiunge un link CSS"""
        self.css_links.append(href)
        return self
    
    def add_js(self, src: str) -> 'ChartPage':
        """Aggiunge un link JavaScript"""
        self.js_links.append(src)
        return self
    
    def build(self) -> HtmlElement:
        """Costruisce la pagina completa con i grafici"""
        from .html import Html, Head, Body, Title, Meta, Link, Script, Div, H1
        from .config import CSSClasses
        
        # Head con librerie
        head_elements = [
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Title(self.title)
        ]
        
        # CSS
        for css_href in self.css_links:
            head_elements.append(Link(rel="stylesheet", href=css_href))
        
        head = Head(head_elements)
        
        # Body con grafici
        body_content = [
            Div([
                H1(self.title, classes=[CSSClasses.DISPLAY_4, CSSClasses.TEXT_CENTER, CSSClasses.MB_5])
            ], classes=[CSSClasses.CONTAINER, CSSClasses.MT_4])
        ]
        
        # Container per i grafici
        charts_container = Div(classes=[CSSClasses.CONTAINER])
        
        # Crea righe per i grafici (2 grafici per riga)
        current_row = None
        for i, chart in enumerate(self.charts):
            # Ogni 2 grafici, crea una nuova riga
            if i % 2 == 0:
                current_row = Div(classes=[CSSClasses.ROW])
                charts_container.add_child(current_row)
            
            # Wrapper per ogni grafico
            chart_wrapper = Div([
                Div([chart], classes=["d-flex", "justify-content-center"])
            ], classes=[CSSClasses.COL_MD_6, CSSClasses.MB_4])
            
            current_row.add_child(chart_wrapper)
        
        body_content.append(charts_container)
        
        body = Body(body_content)
        
        # JavaScript
        for js_src in self.js_links:
            body.add_child(Script(src=js_src))
        
        # Script di inizializzazione per ogni grafico
        for chart in self.charts:
            script_content = chart.get_init_script()
            body.add_child(Script(script_content))
        
        # HTML completo
        html = Html([head, body])
        html.set_attribute('lang', 'it')
        
        return html


# Funzioni helper per creare grafici rapidamente
def quick_line_chart(chart_id: str, labels: List[str], data: List[float], 
                    label: str = "Dataset", color: str = "#36A2EB") -> ChartJS:
    """Crea rapidamente un grafico a linee"""
    chart = ChartJS(chart_id)
    
    # Aggiungi trasparenza al colore in modo sicuro con f-string
    # Evita di usare operazioni di stringa che potrebbero causare problemi
    background_color = f"{color}20"  # Aggiunge "20" al colore per trasparenza
    
    dataset = {
        "label": label,
        "data": data,
        "borderColor": color,
        "backgroundColor": background_color,
        "fill": False
    }
    return chart.line_chart(labels, [dataset])


def quick_bar_chart(chart_id: str, labels: List[str], data: List[float], 
                   label: str = "Dataset", color: str = "#36A2EB") -> ChartJS:
    """Crea rapidamente un grafico a barre"""
    chart = ChartJS(chart_id)
    dataset = {
        "label": label,
        "data": data,
        "backgroundColor": color,
        "borderColor": color,
        "borderWidth": 1
    }
    return chart.bar_chart(labels, [dataset])


def quick_pie_chart(chart_id: str, labels: List[str], data: List[float]) -> ChartJS:
    """Crea rapidamente un grafico a torta"""
    chart = ChartJS(chart_id)
    return chart.pie_chart(labels, data)


# Dati di esempio per test
SAMPLE_DATA = {
    "monthly_sales": {
        "labels": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu"],
        "data": [12, 19, 3, 5, 2, 3]
    },
    "product_categories": {
        "labels": ["Elettronica", "Abbigliamento", "Casa", "Sport", "Libri"],
        "data": [30, 25, 20, 15, 10]
    },
    "quarterly_revenue": {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "data": [15000, 22000, 18000, 28000]
    }
}
