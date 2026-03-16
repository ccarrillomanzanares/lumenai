import time
import json
from datetime import datetime
import os
from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any
from analyzer import SystemAnalyzer
from database import get_db, Metric, Alert
from notifier import send_notification
from auth import verify_jwt_token, create_jwt_token
from fastapi import HTTPException

app = FastAPI(title="LumenAI Server API")
analyzer = SystemAnalyzer()

# Asegurar que existe el directorio de archivos estáticos
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Umbral crítico de CPU para activar IA
CPU_CRITICAL_THRESHOLD = 90.0
AGENT_SECRET = os.getenv("AGENT_SECRET", "default-agent-secret")

class MetricsPayload(BaseModel):
    timestamp: float
    metrics: Dict[str, Any]
    logs: str

class AuthPayload(BaseModel):
    agent_secret: str

@app.post("/auth/token")
async def login(payload: AuthPayload):
    if payload.agent_secret != AGENT_SECRET:
        raise HTTPException(status_code=401, detail="Invalid agent secret")
    token = create_jwt_token({"sub": "agent"})
    return {"access_token": token, "token_type": "bearer"}

def trigger_ai_analysis(metrics: dict, logs: str):
    print("Iniciando análisis SRE en segundo plano...")
    analysis = analyzer.analyze_critical_state(metrics, logs)
    
    # Guardar la alerta en la base de datos
    db = next(get_db())
    new_alert = Alert(
        timestamp=datetime.utcnow(),
        issue_detected=analysis.get('issue_detected', 'Desconocido'),
        root_cause=analysis.get('root_cause', 'Desconocida'),
        recommendations=json.dumps(analysis.get('recommendations', [])),
        raw_metrics=json.dumps(metrics)
    )
    db.add(new_alert)
    db.commit()
    db.close()
    
    # Enviar notificación
    title = f"ALERTA CRÍTICA: {analysis.get('issue_detected', 'Problema detectado')}"
    recs = '\n- '.join(analysis.get('recommendations', []))
    message = f"*Causa Raíz:* {analysis.get('root_cause', 'Desconocida')}\n\n*Recomendaciones:*\n- {recs}"
    send_notification(title, message)
    
    print("\n--- Nuevo Diagnóstico SRE (JSON) guardado en BD ---")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
    print("--------------------------------------\n")


@app.post("/metrics")
async def receive_metrics(payload: MetricsPayload, background_tasks: BackgroundTasks, db: Session = Depends(get_db), token: dict = Depends(verify_jwt_token)):
    cpu_usage = payload.metrics.get('cpu_percent', 0.0)
    memory_usage = payload.metrics.get('memory', {}).get('percent', 0.0)
    disk_usage = payload.metrics.get('disk', {}).get('percent', 0.0)

    # Guardar métrica en la base de datos
    new_metric = Metric(
        timestamp=datetime.utcfromtimestamp(payload.timestamp),
        cpu_percent=cpu_usage,
        memory_percent=memory_usage,
        disk_percent=disk_usage,
        raw_data=json.dumps(payload.metrics)
    )
    db.add(new_metric)
    db.commit()

    # Verificar umbral
    if cpu_usage > CPU_CRITICAL_THRESHOLD:
        print(f"¡ESTADO CRÍTICO DETECTADO (CPU: {cpu_usage}%)! Solicitando análisis a Gemini...")
        background_tasks.add_task(trigger_ai_analysis, payload.metrics, payload.logs)
        return {"status": "Critical", "message": "Análisis IA en proceso"}
        
    return {"status": "OK"}

@app.get("/alerts")
async def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(20).all()
    return {"active_alerts": alerts}

@app.get("/status")
async def get_status(db: Session = Depends(get_db)):
    latest = db.query(Metric).order_by(Metric.timestamp.desc()).first()
    if not latest:
        return {"status": "No data available"}
    return {"latest_metrics": json.loads(latest.raw_data)}

@app.get("/history")
async def get_history(limit: int = 30, db: Session = Depends(get_db)):
    metrics = db.query(Metric).order_by(Metric.timestamp.desc()).limit(limit).all()
    # Invertir para devolver orden cronológico a la gráfica
    return {"history": [{"time": m.timestamp.isoformat(), "cpu": m.cpu_percent, "memory": m.memory_percent} for m in reversed(metrics)]}

@app.get("/")
async def serve_dashboard():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    # Ejecutar servidor embebido
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
