from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.sql import func
from ..database import Base

class Trabajo(Base):
    __tablename__ = "trabajos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    cliente = Column(String(255), nullable=True)
    ubicacion = Column(String(255), nullable=True)
    tipo_servicio = Column(String(255), nullable=True)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    duracion_horas = Column(Float, nullable=True)
    costo = Column(Float, nullable=True)
    estado = Column(String(50), default="pendiente")  # pendiente, en_progreso, completado
    notas = Column(Text, nullable=True)
    imagenes = Column(JSON, nullable=True)  # Lista de URLs de imágenes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)
