from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class TestimonioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    empresa: Optional[str] = None
    cargo: Optional[str] = None
    testimonio: str = Field(..., min_length=1)
    calificacion: int = Field(default=5, ge=1, le=5)
    imagen: Optional[str] = None

class TestimonioCreate(TestimonioBase):
    pass

class TestimonioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    empresa: Optional[str] = None
    cargo: Optional[str] = None
    testimonio: Optional[str] = Field(None, min_length=1)
    calificacion: Optional[int] = Field(None, ge=1, le=5)
    imagen: Optional[str] = None
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None

class TestimonioResponse(BaseModel):
    id: int
    name: str = Field(..., validation_alias='nombre')
    email: Optional[EmailStr] = Field(None, validation_alias='email')
    company: Optional[str] = Field(None, validation_alias='empresa')
    position: Optional[str] = Field(None, validation_alias='cargo')
    content: str = Field(..., validation_alias='testimonio')
    rating: int = Field(default=5, validation_alias='calificacion')
    imagen: Optional[str] = None
    is_active: bool
    is_approved: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class TestimonioList(BaseModel):
    items: list[TestimonioResponse]
    total: int


# Esquemas para Invitaciones de Testimonios
class InvitacionCreate(BaseModel):
    """Esquema para crear una invitación de testimonio"""
    email: Optional[EmailStr] = None
    nombre: Optional[str] = Field(None, max_length=255)
    expires_days: int = Field(default=7, ge=1, le=30, description="Días hasta que expire la invitación")


class InvitacionResponse(BaseModel):
    """Esquema de respuesta para invitación de testimonio"""
    id: int
    token: str
    email: Optional[str] = None
    nombre: Optional[str] = None
    used: bool
    expires_at: datetime
    created_at: datetime
    used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvitacionList(BaseModel):
    """Esquema para lista de invitaciones"""
    items: list[InvitacionResponse]
    total: int
