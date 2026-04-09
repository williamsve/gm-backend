from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models.configuracion import Configuracion
from ..utils.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/configuracion", tags=["Configuración"])

# Schema para actualizar configuración
class ConfiguracionUpdate(BaseModel):
    email_notificaciones: bool = True
    reporte_semanal: bool = True

@router.get("/")
def get_configuracion(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener configuración actual"""
    config = db.query(Configuracion).first()
    if not config:
        # Crear configuración por defecto si no existe
        config = Configuracion(
            email_notificaciones=True,
            reporte_semanal=True
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    
    return {
        "email_notificaciones": config.email_notificaciones,
        "reporte_semanal": config.reporte_semanal
    }

@router.post("/")
def update_configuracion(
    configuracion: ConfiguracionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar configuración"""
    config = db.query(Configuracion).first()
    
    if not config:
        # Crear configuración por defecto si no existe
        config = Configuracion(
            email_notificaciones=configuracion.email_notificaciones,
            reporte_semanal=configuracion.reporte_semanal
        )
        db.add(config)
    else:
        # Actualizar configuración existente
        config.email_notificaciones = configuracion.email_notificaciones
        config.reporte_semanal = configuracion.reporte_semanal
    
    db.commit()
    db.refresh(config)
    
    return {
        "message": "Configuración guardada exitosamente",
        "email_notificaciones": config.email_notificaciones,
        "reporte_semanal": config.reporte_semanal
    }