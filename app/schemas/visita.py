from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VisitaBase(BaseModel):
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    pagina: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    region: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class VisitaCreate(VisitaBase):
    pass

class VisitaResponse(VisitaBase):
    id: int
    fecha: datetime

    class Config:
        from_attributes = True

class EstadisticasVisitas(BaseModel):
    total_visitas: int
    visitas_por_mes: dict
    visitas_por_pais: dict
    visitas_por_ciudad: dict
    visitas_recientes: list
