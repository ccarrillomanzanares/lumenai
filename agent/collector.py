import psutil
import time
import os
import subprocess
from typing import Dict, Any

class SystemCollector:
    def __init__(self, log_path: str = "/var/log/syslog", lines_to_read: int = 50):
        self.log_path = log_path
        self.lines_to_read = lines_to_read

    def get_system_metrics(self) -> Dict[str, Any]:
        """Recopila métricas actuales de CPU, Memoria, Disco y Red."""
        metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict(),
            "network": psutil.net_io_counters()._asdict()
        }
        return metrics

    def get_recent_logs(self) -> str:
        """Obtiene las últimas líneas del log del sistema."""
        if not os.path.exists(self.log_path):
            return f"Error: Archivo de log no encontrado en {self.log_path}"
        
        try:
            # Usar tail para ser eficientes con archivos grandes
            result = subprocess.run(
                ['tail', '-n', str(self.lines_to_read), self.log_path],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error leyendo logs: {e}"
        except Exception as e:
             return f"Error inesperado leyendo logs: {e}"

    def collect(self) -> Dict[str, Any]:
        """Recopila todas las métricas y logs."""
        return {
            "timestamp": time.time(),
            "metrics": self.get_system_metrics(),
            "logs": self.get_recent_logs()
        }

if __name__ == "__main__":
    collector = SystemCollector()
    print("Iniciando recolección de métricas. Presiona Ctrl+C para detener.")
    try:
        while True:
            data = collector.collect()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] CPU: {data['metrics']['cpu_percent']}% | RAM: {data['metrics']['memory']['percent']}%")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nRecolección detenida.")
