# Plan de Desarrollo Futuro: lumenai

## Fase 8: Mapas de Dependencias y Relaciones de Red
- [x] **Tarea 8.1:** Modificar el agente recolector (`collector.py`) para extraer las conexiones de red activas. Debe capturar el listado de conexiones de entrada y salida (hosts remotos y puertos locales/remotos con los que se comunica).
- [x] **Tarea 8.2:** Almacenar y consolidar las conexiones de red en el servidor (pendiente de definir la estructura de la base de datos para esto).
- [x] **Tarea 8.3:** Diseñar la interfaz y el modelo de datos para generar y visualizar "Mapas de Relación". El objetivo es que la UI dibuje automáticamente la topología de red, conectando los servicios y procesos que hablan entre los diferentes hosts monitorizados.
