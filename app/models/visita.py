from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base

class Visita(Base):
    __tablename__ = "visitas"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    pagina = Column(String(200), nullable=True)
    pais = Column(String(100), nullable=True)
    ciudad = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Visita(id={self.id}, pagina='{self.pagina}', pais='{self.pais}', fecha='{self.fecha}')>"
