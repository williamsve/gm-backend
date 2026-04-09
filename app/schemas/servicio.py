from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Esquemas para request
class ServicioCreate(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    descripcion: str = Field(..., min_length=3, max_length=500)
    imagen: Optional[str] = Field(None, max_length=500)

class ServicioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, min_length=3, max_length=500)
    imagen: Optional[str] = Field(None, max_length=500)

# Esquemas para response
class ServicioResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    imagen: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ServicioList(BaseModel):
    items: list[ServicioResponse]
    total: int
