from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base

class Servicio(Base):
    __tablename__ = "servicios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    imagen = Column(String(500), default="/placeholder.jpg")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)
    
    def __repr__(self):
        return f"<Servicio(id={self.id}, nombre={self.nombre})>"
