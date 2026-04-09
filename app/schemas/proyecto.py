from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProyectoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    imagen: Optional[str] = None
    cliente: Optional[str] = None
    ubicacion: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    estado: str = Field(default="pendiente")

class ProyectoCreate(ProyectoBase):
    pass

class ProyectoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    descripcion: Optional[str] = None
    imagen: Optional[str] = None
    cliente: Optional[str] = None
    ubicacion: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    estado: Optional[str] = None
    is_active: Optional[bool] = None

class ProyectoResponse(ProyectoBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProyectoList(BaseModel):
    items: list[ProyectoResponse]
    total: int
