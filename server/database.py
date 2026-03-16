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
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_percent = Column(Float)
    raw_data = Column(Text) # Guardamos el payload JSON completo por si acaso

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    issue_detected = Column(String)
    root_cause = Column(Text)
    recommendations = Column(Text) # JSON de las recomendaciones
    raw_metrics = Column(Text)

# Crea las tablas si no existen
Base.metadata.create_all(bind=engine)

# Inyector de dependencias para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
