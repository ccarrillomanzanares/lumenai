import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# Crea una base de datos SQLite local dentro de la carpeta server
DATABASE_URL = "sqlite:///./lumenai.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, index=True, default="Unknown")
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_percent = Column(Float)
    raw_data = Column(Text) # Guardamos el payload JSON completo por si acaso

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, index=True, default="Unknown")
    timestamp = Column(DateTime, default=datetime.utcnow)
    issue_detected = Column(String)
    root_cause = Column(Text)
    recommendations = Column(Text) # JSON de las recomendaciones
    raw_metrics = Column(Text)

class PendingAnalysis(Base):
    __tablename__ = "pending_analyses"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metrics_json = Column(Text)
    logs_text = Column(Text)
    status = Column(String, default="pending") # pending, approved, rejected

class NetworkConnection(Base):
    __tablename__ = "network_connections"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, index=True)
    local_address = Column(String)
    remote_address = Column(String, nullable=True)
    status = Column(String)
    protocol = Column(String) # TCP, UDP
    pid = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Crea las tablas si no existen
Base.metadata.create_all(bind=engine)

# Inyector de dependencias para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
