from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from ..database import Base

class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    imagen = Column(String(500), nullable=True)
    cliente = Column(String(255), nullable=True)
    ubicacion = Column(String(255), nullable=True)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    estado = Column(String(50), default="pendiente")  # pendiente, en_progreso, completado
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)
