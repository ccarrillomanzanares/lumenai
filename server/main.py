import time
import json
from datetime import datetime, timedelta
import os
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
from analyzer import SystemAnalyzer
from database import get_db, Metric, Alert, PendingAnalysis, NetworkConnection
from notifier import send_notification
from auth import verify_jwt_token, create_jwt_token

app = FastAPI(title="LumenAI Server API")
analyzer = SystemAnalyzer()

# Estado de configuración global
settings = {
    "auto_analyze_enabled": False
}

# Asegurar que existe el directorio de archivos estáticos
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Umbral crítico de CPU para activar IA
CPU_CRITICAL_THRESHOLD = 90.0
AGENT_SECRET = os.getenv("AGENT_SECRET", "default-agent-secret")

class MetricsPayload(BaseModel):
    timestamp: float
    hostname: str = "Unknown"
    metrics: Dict[str, Any]
    logs: str

class AuthPayload(BaseModel):
    agent_secret: str

class SettingsPayload(BaseModel):
    auto_analyze_enabled: bool

@app.get("/settings")
async def get_settings():
    return settings

@app.post("/settings")
async def update_settings(payload: SettingsPayload):
    settings["auto_analyze_enabled"] = payload.auto_analyze_enabled
    return {"message": "Configuración actualizada", "settings": settings}

@app.post("/auth/token")
async def login(payload: AuthPayload):
    if payload.agent_secret != AGENT_SECRET:
        raise HTTPException(status_code=401, detail="Invalid agent secret")
    token = create_jwt_token({"sub": "agent"})
    return {"access_token": token, "token_type": "bearer"}

def trigger_ai_analysis(hostname: str, metrics: dict, logs: str):
    print(f"Iniciando análisis SRE en segundo plano para {hostname}...")
    analysis = analyzer.analyze_critical_state(metrics, logs)
    
    # Guardar la alerta en la base de datos
    db = next(get_db())
    new_alert = Alert(
        hostname=hostname,
        timestamp=datetime.utcnow(),
        issue_detected=analysis.get('issue_detected', 'Desconocido'),
        root_cause=analysis.get('root_cause', 'Desconocida'),
        recommendations=json.dumps(analysis.get('recommendations', [])),
        raw_metrics=json.dumps(metrics)
    )
    db.add(new_alert)
    db.commit()
    db.close()
    
    # Enviar notificación de resultado
    title = f"ALERTA CRÍTICA [{hostname}]: {analysis.get('issue_detected', 'Problema detectado')}"
    recs = '\n- '.join(analysis.get('recommendations', []))
    message = f"*Causa Raíz:* {analysis.get('root_cause', 'Desconocida')}\n\n*Recomendaciones:*\n- {recs}"
    send_notification(title, message)
    
    print(f"\n--- Nuevo Diagnóstico SRE (JSON) guardado en BD para {hostname} ---")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
    print("--------------------------------------\n")


@app.post("/metrics")
async def receive_metrics(payload: MetricsPayload, background_tasks: BackgroundTasks, db: Session = Depends(get_db), token: dict = Depends(verify_jwt_token)):
    cpu_usage = payload.metrics.get('cpu_percent', 0.0)
    memory_usage = payload.metrics.get('memory', {}).get('percent', 0.0)
    disk_usage = payload.metrics.get('disk', {}).get('percent', 0.0)

    # Guardar métrica en la base de datos
    new_metric = Metric(
        hostname=payload.hostname,
        timestamp=datetime.utcfromtimestamp(payload.timestamp),
        cpu_percent=cpu_usage,
        memory_percent=memory_usage,
        disk_percent=disk_usage,
        raw_data=json.dumps(payload.metrics)
    )
    db.add(new_metric)

    # Actualizar Conexiones de Red (Fase 8)
    net_conns = payload.metrics.get('network_connections', [])
    if net_conns:
        # Borrar conexiones anteriores de este host para mantener solo el estado actual
        db.query(NetworkConnection).filter(NetworkConnection.hostname == payload.hostname).delete()
        
        # Insertar nuevas conexiones
        for conn in net_conns:
            db.add(NetworkConnection(
                hostname=payload.hostname,
                local_address=conn.get('local_address'),
                remote_address=conn.get('remote_address'),
                status=conn.get('status'),
                protocol=conn.get('type'),
                pid=conn.get('pid'),
                timestamp=datetime.utcfromtimestamp(payload.timestamp)
            ))
    
    db.commit()

    # Verificar umbral
    if cpu_usage > CPU_CRITICAL_THRESHOLD:
        if settings.get("auto_analyze_enabled", False):
            # TAREA 6.2: Modo Automático -> Ejecutar IA directamente
            print(f"¡ESTADO CRÍTICO DETECTADO en {payload.hostname} (CPU: {cpu_usage}%)! Ejecutando análisis automático...")
            background_tasks.add_task(trigger_ai_analysis, payload.hostname, payload.metrics, payload.logs)
            return {"status": "Critical", "message": "Análisis IA automático iniciado"}
        else:
            # TAREA 6.1: Modo Human-in-the-loop -> Crear solicitud pendiente
            five_mins_ago = datetime.utcnow() - timedelta(minutes=5)
            recent_pending = db.query(PendingAnalysis).filter(
                PendingAnalysis.hostname == payload.hostname,
                PendingAnalysis.status == "pending",
                PendingAnalysis.timestamp >= five_mins_ago
            ).first()

            if not recent_pending:
                print(f"¡ESTADO CRÍTICO DETECTADO en {payload.hostname} (CPU: {cpu_usage}%)! Creando solicitud de análisis pendiente...")
                new_pending = PendingAnalysis(
                    hostname=payload.hostname,
                    timestamp=datetime.utcnow(),
                    metrics_json=json.dumps(payload.metrics),
                    logs_text=payload.logs,
                    status="pending"
                )
                db.add(new_pending)
                db.commit()
                
                # Notificar que se requiere aprobación humana
                send_notification(
                    f"⚠️ Requiere Aprobación SRE [{payload.hostname}]", 
                    f"Se detectó CPU crítica ({cpu_usage}%). Se han guardado los logs y métricas. Por favor, aprueba el análisis IA desde el Dashboard.",
                    level="warning"
                )
                return {"status": "Critical", "message": "Análisis pendiente de aprobación SRE"}
            else:
                 return {"status": "Critical", "message": "Ya existe una solicitud de análisis reciente"}
        
    return {"status": "OK"}

# --- Nuevos Endpoints para Tarea 6.1 ---

@app.get("/pending_analyses")
async def get_pending_analyses(hostname: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(PendingAnalysis).filter(PendingAnalysis.status == "pending")
    if hostname:
        query = query.filter(PendingAnalysis.hostname == hostname)
    pending = query.order_by(PendingAnalysis.timestamp.desc()).all()
    return {"pending_analyses": [
        {"id": p.id, "hostname": p.hostname, "timestamp": p.timestamp.isoformat()} for p in pending
    ]}

@app.post("/pending_analyses/{analysis_id}/approve")
async def approve_analysis(analysis_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    pending = db.query(PendingAnalysis).filter(PendingAnalysis.id == analysis_id).first()
    if not pending or pending.status != "pending":
        raise HTTPException(status_code=404, detail="Pending analysis not found or already processed")
    
    pending.status = "approved"
    db.commit()
    
    # Iniciar el análisis de Gemini con los datos capturados en el momento del fallo
    metrics = json.loads(pending.metrics_json)
    background_tasks.add_task(trigger_ai_analysis, pending.hostname, metrics, pending.logs_text)
    return {"message": "Análisis aprobado e iniciado"}

@app.post("/pending_analyses/{analysis_id}/reject")
async def reject_analysis(analysis_id: int, db: Session = Depends(get_db)):
    pending = db.query(PendingAnalysis).filter(PendingAnalysis.id == analysis_id).first()
    if not pending or pending.status != "pending":
        raise HTTPException(status_code=404, detail="Pending analysis not found or already processed")
    
    pending.status = "rejected"
    db.commit()
    return {"message": "Análisis rechazado"}

# ----------------------------------------

@app.get("/hosts")
async def get_hosts(db: Session = Depends(get_db)):
    # Obtener lista de hosts distintos que han reportado métricas
    hosts = db.query(Metric.hostname).distinct().all()
    return {"hosts": [h[0] for h in hosts]}

@app.get("/network_map")
async def get_network_map(db: Session = Depends(get_db)):
    # Obtener todas las conexiones de red de todos los hosts
    conns = db.query(NetworkConnection).all()
    
    # Consolidar nodos y enlaces
    nodes_map = {} # id -> {id, type}
    links = []
    
    # Obtener lista de hosts internos conocidos
    internal_hosts = [h[0] for h in db.query(Metric.hostname).distinct().all()]
    
    # 1. Identificar puertos en escucha por host para determinar si el tráfico es de entrada o salida
    listening_ports_by_host = {}
    for c in conns:
        if c.status == 'LISTEN':
            port = c.local_address.split(':')[-1] if ':' in c.local_address else None
            if port:
                if c.hostname not in listening_ports_by_host:
                    listening_ports_by_host[c.hostname] = set()
                listening_ports_by_host[c.hostname].add(port)

    # 2. Construir nodos y enlaces
    for c in conns:
        source = c.hostname
        target = c.remote_address
        
        # Registrar nodo origen (siempre es un host monitorizado)
        if source not in nodes_map:
            nodes_map[source] = {"id": source, "type": "host"}
        
        # Ignorar las conexiones en LISTEN (el usuario pidió no mostrar los puertos del cliente en el mapa directamente)
        if c.status == 'LISTEN':
            continue

        if target:
            target_id = target
            
            # Registrar nodo destino
            if target_id not in nodes_map:
                # Comprobar si la IP del target corresponde a uno de nuestros hosts conocidos
                target_ip = target.split(':')[0] if ':' in target else target
                is_internal = target_ip in internal_hosts
                nodes_map[target_id] = {
                    "id": target_id, 
                    "type": "host" if is_internal else "external"
                }
            
            # Determinar dirección de la conexión
            local_port = c.local_address.split(':')[-1] if ':' in c.local_address else None
            is_inbound = False
            
            # Si el puerto local de la conexión es uno de los puertos en los que este host escucha,
            # entonces alguien (target) se conectó a nosotros (source). Es tráfico entrante.
            if c.hostname in listening_ports_by_host and local_port in listening_ports_by_host[c.hostname]:
                is_inbound = True
                
            if is_inbound:
                link_source = target_id
                link_target = source
            else:
                link_source = source
                link_target = target_id
            
            # Crear enlace con la dirección correcta
            links.append({
                "source": link_source,
                "target": link_target,
                "status": c.status,
                "protocol": c.protocol
            })
            
    return {
        "nodes": list(nodes_map.values()),
        "links": links
    }

@app.get("/alerts")
async def get_alerts(hostname: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Alert)
    if hostname:
        query = query.filter(Alert.hostname == hostname)
    alerts = query.order_by(Alert.timestamp.desc()).limit(20).all()
    return {"active_alerts": alerts}

@app.get("/status")
async def get_status(hostname: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Metric)
    if hostname:
        query = query.filter(Metric.hostname == hostname)
    latest = query.order_by(Metric.timestamp.desc()).first()
    if not latest:
        return {"status": "No data available"}
    return {"latest_metrics": json.loads(latest.raw_data)}

@app.get("/history")
async def get_history(limit: int = 30, hostname: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Metric)
    if hostname:
        query = query.filter(Metric.hostname == hostname)
    metrics = query.order_by(Metric.timestamp.desc()).limit(limit).all()
    # Invertir para devolver orden cronológico a la gráfica
    return {"history": [{"time": m.timestamp.isoformat(), "cpu": m.cpu_percent, "memory": m.memory_percent} for m in reversed(metrics)]}

@app.get("/")
async def serve_dashboard():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    # Ejecutar servidor embebido
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
