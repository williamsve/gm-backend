from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from ..database import Base

class Testimonio(Base):
    __tablename__ = "testimonios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    empresa = Column(String(255), nullable=True)
    cargo = Column(String(255), nullable=True)
    testimonio = Column(Text, nullable=False)
    calificacion = Column(Integer, default=5)  # 1-5 estrellas
    imagen = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InvitacionTestimonio(Base):
    """Modelo para tokens de invitación de testimonios"""
    __tablename__ = "invitaciones_testimonio"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=True)
    nombre = Column(String(255), nullable=True)
    used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)
