from sqlalchemy import Column, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base

class Configuracion(Base):
    __tablename__ = "configuracion"
    
    id = Column(Integer, primary_key=True, index=True)
    email_notificaciones = Column(Boolean, default=True)
    reporte_semanal = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Configuracion(id={self.id})>"