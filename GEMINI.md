# Plan de Desarrollo: lumenai - Herramienta de Monitorización AI-Native

## Fase 1: Cimientos y Recolección de Datos
- [x] **Tarea 1.1:** Configurar el entorno de Python y la autenticación con la API Key de Gemini.
- [x] **Tarea 1.2:** Crear un módulo `collector.py` usando la librería `psutil` para obtener métricas de sistema (CPU, Memoria, Disco, Red) cada 10 segundos.
- [x] **Tarea 1.3:** Implementar un capturador de logs que lea las últimas líneas de `/var/log/syslog` (o el log de eventos en Windows).

## Fase 2: Integración con Gemini CLI (Análisis Inteligente)
- [x] **Tarea 2.1:** Diseñar un "System Prompt" que defina el rol de Gemini como experto en SRE (Site Reliability Engineering).
- [x] **Tarea 2.2:** Crear el script `analyzer.py` que envíe ráfagas de métricas y logs a Gemini cuando se detecte un umbral crítico (ej. CPU > 90%).
- [x] **Tarea 2.3:** Programar la lógica para que Gemini devuelva una sugerencia de reparación en formato JSON.

## Fase 3: Interfaz y Alertas
- [x] **Tarea 3.1:** Crear una CLI interactiva que muestre el estado del sistema en tiempo real.
- [x] **Tarea 3.2:** Implementar un sistema de notificaciones simple que imprima las recomendaciones de la IA en la consola con formato Markdown.

## Fase 4: Refactorización y Documentación
- [x] **Tarea 4.1:** Generar el archivo `requirements.txt`.
- [x] **Tarea 4.2:** Escribir la documentación técnica sobre cómo extender los agentes de recolección.

## Fase 5: Arquitectura Distribuida (Cliente/Servidor)
- [x] **Tarea 5.1:** Reestructuración de la Arquitectura (Agentes Ligeros y Servidor Centralizado API).
- [x] **Tarea 5.2:** Persistencia de Datos (Base de datos para almacenar métricas y análisis).
- [x] **Tarea 5.3:** Interfaz Gráfica del Servidor (Dashboard Web para monitorización global).
- [x] **Tarea 5.4:** Sistema de Alertas y Notificaciones (Integraciones externas como Slack, Email o Telegram).
- [x] **Tarea 5.5:** Seguridad y Autenticación (Comunicación encriptada y tokens JWT para los agentes).

