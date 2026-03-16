# Pruebas de la Arquitectura Cliente/Servidor de LumenAI

Para probar la nueva arquitectura distribuida, necesitarás abrir dos terminales diferentes.

## 1. Levantar el Servidor (Terminal 1)

El servidor escuchará en el puerto 8000 y será el encargado de recibir métricas y comunicarse con Gemini.

```bash
cd /home/ccmai/lumenai/server
source ../venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Una vez levantado, podrás visitar el dashboard interactivo de la API generado automáticamente por FastAPI en:
[http://localhost:8000/docs](http://localhost:8000/docs)

## 2. Levantar el Agente (Terminal 2)

El agente debe ejecutarse en la máquina que deseas monitorizar (para esta prueba, tu misma máquina local).

```bash
cd /home/ccmai/lumenai/agent
source ../venv/bin/activate
python client.py
```

En la salida del agente verás cómo envía las métricas al servidor cada 10 segundos, y en la terminal del servidor verás las peticiones POST entrantes.

## 3. Verificar el histórico y las alertas

Puedes hacer peticiones GET a las siguientes rutas desde el navegador o usando curl:
- **Estado actual:** [http://localhost:8000/status](http://localhost:8000/status)
- **Historial de Alertas de IA:** [http://localhost:8000/alerts](http://localhost:8000/alerts)