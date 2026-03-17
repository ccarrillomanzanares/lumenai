import psutil
import time
import os
import subprocess
from typing import Dict, Any

class SystemCollector:
    def __init__(self, log_path: str = "/var/log/syslog", lines_to_read: int = 50):
        self.log_path = log_path
        self.lines_to_read = lines_to_read
        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = time.time()

    def get_system_metrics(self) -> Dict[str, Any]:
        """Recopila métricas actuales de CPU, Memoria, Disco y Red."""
        # 1. Velocidad de red
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        time_diff = current_time - self.last_net_time
        if time_diff > 0:
            bytes_sent_sec = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff
            bytes_recv_sec = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff
        else:
            bytes_sent_sec = 0
            bytes_recv_sec = 0
            
        self.last_net_io = current_net_io
        self.last_net_time = current_time

        # 2. Carga Media (Load Average)
        try:
            load_avg = os.getloadavg()
        except AttributeError:
            load_avg = (0.0, 0.0, 0.0) # Fallback para Windows

        # 3. Top Procesos
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        top_processes = sorted(processes, key=lambda p: p.get('cpu_percent', 0) or 0, reverse=True)[:5]

        # 4. Conexiones de Red (Fase 8)
        connections = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                # Solo nos interesan conexiones con dirección remota (entrada/salida) o en LISTEN
                if conn.raddr or conn.status == 'LISTEN':
                    conn_info = {
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status,
                        "family": "IPv4" if conn.family == 2 else "IPv6",
                        "type": "TCP" if conn.type == 1 else "UDP",
                        "pid": conn.pid
                    }
                    connections.append(conn_info)
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

        # 5. Métricas expandidas
        metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory()._asdict(),
            "swap": psutil.swap_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict(),
            "network": current_net_io._asdict(),
            "network_rates": {
                "bytes_sent_sec": bytes_sent_sec,
                "bytes_recv_sec": bytes_recv_sec
            },
            "network_connections": connections,
            "load_average": load_avg,
            "top_processes": top_processes
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
        import socket
        return {
            "timestamp": time.time(),
            "hostname": socket.gethostname(),
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
