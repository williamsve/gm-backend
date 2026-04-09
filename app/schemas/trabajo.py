from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TrabajoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    cliente: Optional[str] = None
    ubicacion: Optional[str] = None
    tipo_servicio: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    duracion_horas: Optional[float] = None
    costo: Optional[float] = None
    estado: str = Field(default="pendiente")
    notas: Optional[str] = None
    imagenes: Optional[List[str]] = None  # Lista de URLs de imágenes

class TrabajoCreate(TrabajoBase):
    pass

class TrabajoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    descripcion: Optional[str] = None
    cliente: Optional[str] = None
    ubicacion: Optional[str] = None
    tipo_servicio: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    duracion_horas: Optional[float] = None
    costo: Optional[float] = None
    estado: Optional[str] = None
    notas: Optional[str] = None
    imagenes: Optional[List[str]] = None  # Lista de URLs de imágenes
    is_active: Optional[bool] = None

class TrabajoResponse(TrabajoBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TrabajoList(BaseModel):
    items: list[TrabajoResponse]
    total: int
