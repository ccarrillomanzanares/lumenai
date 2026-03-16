# Extensión de Agentes de Recolección en LumenAI

LumenAI está diseñado para ser modular. Puedes extender la capacidad de monitorización añadiendo nuevos métodos de recolección al `SystemCollector` o creando nuevos módulos.

## 1. Añadir nuevas métricas al colector actual

Para añadir métricas de una nueva fuente (por ejemplo, monitorizar la temperatura de la CPU o el estado de un servicio específico), sigue estos pasos:

1. Abre `collector.py`.
2. Añade un nuevo método a la clase `SystemCollector`:

```python
def get_service_status(self, service_name: str) -> str:
    # Lógica para obtener el estado del servicio
    # Ejemplo usando systemctl o psutil
    pass
```

3. Actualiza el método `collect()` para incluir esta nueva información en el diccionario devuelto.

## 2. Crear un nuevo Agente de Recolección

Si deseas monitorizar algo específico como una base de datos (MySQL/PostgreSQL) o contenedores (Docker), te recomendamos crear una nueva clase:

```python
class DockerCollector:
    def collect(self) -> dict:
        # Lógica para usar la API de Docker
        return {"containers_running": 5, "cpu_usage": 12.5}
```

Luego, integra este nuevo colector en `analyzer.py` o `cli.py` para que los datos se envíen a Gemini cuando se detecten anomalías.

## 3. Personalización de Logs

Por defecto, LumenAI lee `/var/log/syslog`. Puedes cambiar la ruta al instanciar `SystemCollector` o modificar el constructor para que acepte una lista de rutas de logs.

```python
collector = SystemCollector(log_path="/var/log/apache2/error.log")
```
