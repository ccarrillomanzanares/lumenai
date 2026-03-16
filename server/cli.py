import time
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.markdown import Markdown
from rich.console import Console
from collector import SystemCollector
from analyzer import SystemAnalyzer

console = Console()

def generate_metrics_table(metrics) -> Table:
    """Genera una tabla de Rich con las métricas actuales."""
    table = Table(show_header=True, header_style="bold cyan", expand=True)
    table.add_column("Métrica", justify="left", style="bold white")
    table.add_column("Valor", justify="right", style="green")

    # Formateo de bytes a MB
    mb_memory_used = metrics['memory']['used'] // (1024**2)
    mb_memory_total = metrics['memory']['total'] // (1024**2)
    
    cpu_color = "red" if metrics['cpu_percent'] > 85 else "green"
    
    table.add_row("CPU", f"[{cpu_color}]{metrics['cpu_percent']}%[/{cpu_color}]")
    table.add_row("Memoria RAM", f"{metrics['memory']['percent']}% ({mb_memory_used} MB / {mb_memory_total} MB)")
    table.add_row("Uso de Disco", f"{metrics['disk']['percent']}%")
    
    return table

def main():
    collector = SystemCollector()
    analyzer = SystemAnalyzer(cpu_threshold=90.0)
    
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", size=8),
        Layout(name="alert", visible=False) # Se mostrará sólo en caso de alerta
    )
    
    layout["header"].update(Panel("LumenAI - Monitorización SRE AI-Native", style="bold white on blue"))
    
    # Iniciar Live dashboard
    with Live(layout, refresh_per_second=2, screen=True) as live:
        try:
            while True:
                data = collector.collect()
                metrics = data["metrics"]
                
                # Actualizar el panel principal con las métricas
                layout["main"].update(
                    Panel(generate_metrics_table(metrics), title="Métricas en Tiempo Real", border_style="cyan")
                )
                
                # Verificar umbral crítico
                if metrics["cpu_percent"] > analyzer.cpu_threshold:
                    layout["alert"].visible = True
                    layout["alert"].update(
                        Panel("⚠️ Estado crítico detectado. Generando diagnóstico con IA (puede tardar unos segundos)...", title="Alerta SRE", style="bold red")
                    )
                    
                    # Ejecutar análisis (esto bloqueará el hilo brevemente mientras responde la API)
                    analysis = analyzer.analyze_critical_state(metrics, data["logs"])
                    
                    if "error" in analysis:
                        md_text = f"**Error de Diagnóstico:**\n\n{analysis['error']}"
                    else:
                        md_text = f"### Problema Detectado\n{analysis.get('issue_detected', 'Desconocido')}\n\n"
                        md_text += f"### Causa Raíz\n{analysis.get('root_cause', 'Desconocida')}\n\n"
                        md_text += "### Recomendaciones de Reparación\n"
                        for rec in analysis.get('recommendations', []):
                            md_text += f"- {rec}\n"
                    
                    # Mostrar la recomendación en Markdown
                    layout["alert"].update(
                        Panel(Markdown(md_text), title="Diagnóstico de IA", border_style="red", padding=(1, 2))
                    )
                    
                    # Pausar temporalmente para que el usuario pueda leer el diagnóstico
                    time.sleep(15) 
                    layout["alert"].visible = False
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            # Salida limpia
            pass

if __name__ == "__main__":
    main()
