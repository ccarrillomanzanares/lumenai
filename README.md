# LumenAI 🌟

**LumenAI** es una herramienta de monitorización de sistemas y Site Reliability Engineering (SRE) *AI-Native*. 
Utiliza agentes ligeros para recolectar métricas detalladas del sistema y logs en tiempo real. Cuando detecta un estado crítico (como un pico inusual de CPU), puede solicitar la intervención de la API de **Google Gemini** para que actúe como un experto SRE, diagnosticando el problema y ofreciendo recomendaciones de resolución (Root Cause Analysis).

## 🚀 Características Principales

- **Arquitectura Distribuida:** Agentes ligeros instalables en cualquier servidor que reportan a una API central.
- **Autenticación Segura:** Comunicación encriptada entre el Agente y el Servidor utilizando tokens JWT.
- **Métricas Extendidas:** Monitorización detallada que incluye CPU, RAM (con Swap y Buffers/Caché), uso de Disco, Load Average, Tráfico de Red (KB/s) y Top Procesos en tiempo real.
- **Mapa de Red Global:** Generación automática de topologías de red interactivas (vía D3.js) que muestran las conexiones y puertos activos entre tus hosts monitorizados y servicios externos.
- **Análisis Inteligente (AI-Native):** Integración con el modelo `gemini-2.5-flash` de Google para el análisis avanzado de logs y métricas anómalas.
- **Modo "Human-in-the-loop" y Autopiloto:** Elige si quieres que la IA diagnostique los problemas automáticamente o si prefieres aprobar manualmente el envío de datos desde el Dashboard cuando se reciba una alerta.
- **Notificaciones Proactivas:** Alertas automáticas vía Webhooks de Slack o Bots de Telegram cuando se detectan incidentes o se requiere aprobación manual.
- **Dashboard en Tiempo Real:** Interfaz gráfica rica con gráficas separadas para recursos, tablas de procesos, y mapa global de relaciones.

---

## 🛠️ Requisitos Previos

- Python 3.10 o superior.
- Una **API Key de Google Gemini** ([Consíguela aquí](https://aistudio.google.com/app/apikey)).
- (Opcional) Webhook de Slack o Token de Bot de Telegram para recibir las notificaciones.

---

## 📦 Instalación y Configuración

1. **Clonar el Repositorio**
   ```bash
   git clone https://github.com/ccarrillomanzanares/lumenai.git
   cd lumenai
   ```

2. **Crear y Activar el Entorno Virtual**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Linux/macOS
   # venv\Scripts\activate   # En Windows
   ```

3. **Instalar Dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar las Variables de Entorno**
   Copia el archivo de ejemplo o crea un `.env` en la raíz del proyecto:
   ```env
   GEMINI_API_KEY=tu_api_key_de_gemini
   JWT_SECRET_KEY=una_clave_secreta_super_segura_de_al_menos_32_caracteres
   AGENT_SECRET=tu_secreto_para_agentes
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/... # Opcional
   TELEGRAM_BOT_TOKEN=tu_token_de_telegram               # Opcional
   TELEGRAM_CHAT_ID=tu_chat_id                           # Opcional
   ```

---

## 🏃‍♂️ Cómo Ejecutar

### 1. Iniciar el Servidor (API Central)
El servidor almacena las métricas, gestiona los tokens JWT y expone el Dashboard interactivo.
```bash
python server/main.py
```
* **Dashboard Web:** `http://localhost:8000`
* **Documentación de la API:** `http://localhost:8000/docs`

### 2. Iniciar el Agente Recolector
En una segunda terminal (o en otro servidor), inicia el agente. Éste recolectará datos locales (CPU, RAM, Top Procesos, conexiones de red) y los enviará al servidor centralizado.
```bash
python agent/client.py
```

### 3. Simulando un Incidente
Si deseas probar el análisis IA, estresa la CPU para que supere el umbral predeterminado del 90%:
* **En Linux/macOS:**
  ```bash
  cat /dev/urandom | gzip -9 > /dev/null
  ```
  *(Presiona `Ctrl + C` para detenerlo después de 10-15 segundos).*
  
Recibirás una notificación (Slack/Telegram) indicando que se requiere aprobación. Entra al Dashboard Web, ve a la vista de Hosts y aprueba el análisis pendiente para que Gemini diagnostique el problema. Puedes cambiar este comportamiento desde la pestaña "Configuración" del Dashboard.

---

## 📁 Estructura del Proyecto

```text
lumenai/
├── agent/                  # Código del agente (cliente ligero)
│   ├── client.py           # Conexión JWT y envío periódico de datos
│   └── collector.py        # Extracción de métricas de OS y red (psutil)
├── server/                 # Servidor y API (FastAPI)
│   ├── main.py             # Endpoints, lógica de negocio y consolidación de red
│   ├── auth.py             # Generación y validación de tokens JWT
│   ├── analyzer.py         # Prompting e integración con Gemini (GenAI)
│   ├── database.py         # Modelos de SQLAlchemy y conexión SQLite
│   ├── notifier.py         # Integración de alertas a Slack/Telegram
│   └── static/             # Dashboard interactivo con Chart.js y D3.js
├── docs/                   # Documentación técnica extra
├── requirements.txt        # Dependencias de Python
└── .env                    # Variables de entorno (No se sube a Git)
```

---
*Construido colaborativamente con IA.*