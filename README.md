# LumenAI 🌟

**LumenAI** es una herramienta de monitorización de sistemas y Site Reliability Engineering (SRE) *AI-Native*. 
Utiliza agentes ligeros para recolectar métricas del sistema (CPU, Memoria, Disco, Red) y logs en tiempo real. Cuando detecta un estado crítico (como un pico inusual de CPU), envía esta información a la API de **Google Gemini** para que actúe como un experto SRE, diagnosticando el problema y ofreciendo recomendaciones de resolución (Root Cause Analysis).

## 🚀 Características Principales

- **Arquitectura Distribuida:** Agentes ligeros instalables en cualquier servidor que reportan a una API central.
- **Autenticación Segura:** Comunicación encriptada entre el Agente y el Servidor utilizando tokens JWT.
- **Análisis Inteligente (AI-Native):** Integración con el modelo `gemini-2.5-flash` de Google para el análisis avanzado de logs y métricas anómalas.
- **Notificaciones Proactivas:** Alertas automáticas vía Webhooks de Slack o Bots de Telegram cuando se detectan incidentes.
- **Dashboard en Tiempo Real:** Interfaz gráfica simple para monitorear el estado de tu infraestructura y visualizar las alertas pasadas.

---

## 🛠️ Requisitos Previos

- Python 3.10 o superior.
- Una **API Key de Google Gemini** ([Consíguela aquí](https://aistudio.google.com/app/apikey)).
- (Opcional) Webhook de Slack o Token de Bot de Telegram para recibir las notificaciones.

---

## 📦 Instalación y Configuración

1. **Clonar el Repositorio**
   ```bash
   git clone https://github.com/TU_USUARIO/lumenai.git
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
   JWT_SECRET_KEY=una_clave_secreta_super_segura
   AGENT_SECRET=tu_secreto_para_agentes
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/... # Opcional
   TELEGRAM_BOT_TOKEN=tu_token_de_telegram               # Opcional
   TELEGRAM_CHAT_ID=tu_chat_id                           # Opcional
   ```

---

## 🏃‍♂️ Cómo Ejecutar

### 1. Iniciar el Servidor (API Central)
El servidor almacena las métricas, gestiona los tokens JWT y expone el Dashboard.
```bash
python server/main.py
```
* **Dashboard Web:** `http://localhost:8000`
* **Documentación de la API:** `http://localhost:8000/docs`

### 2. Iniciar el Agente Recolector
En una segunda terminal (o en otro servidor), inicia el agente. Éste recolectará datos locales y los enviará al servidor centralizado.
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
  
Verás en la consola del servidor cómo se contacta a Gemini, el análisis generado, y recibirás la notificación en Slack/Telegram.

---

## 📁 Estructura del Proyecto

```text
lumenai/
├── agent/                  # Código del agente (cliente ligero)
│   ├── client.py           # Conexión JWT y envío periódico de datos
│   └── collector.py        # Extracción de métricas de OS (psutil)
├── server/                 # Servidor y API (FastAPI)
│   ├── main.py             # Endpoints y lógica de negocio
│   ├── auth.py             # Generación y validación de tokens JWT
│   ├── analyzer.py         # Prompting e integración con Gemini (GenAI)
│   ├── database.py         # Modelos de SQLAlchemy y conexión SQLite
│   ├── notifier.py         # Integración de alertas a Slack/Telegram
│   └── static/             # Archivos HTML/JS para el Dashboard
├── docs/                   # Documentación técnica extra
├── requirements.txt        # Dependencias de Python
└── .env                    # Variables de entorno (No se sube a Git)
```

---
*Construido colaborativamente con IA.*
