from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..database import get_db
from ..models.servicio import Servicio
from ..models.user import User
from ..schemas.servicio import ServicioCreate, ServicioUpdate, ServicioResponse, ServicioList
from ..utils.auth import get_current_admin_user

router = APIRouter(prefix="/api/servicios", tags=["Servicios"])

@router.get("/", response_model=ServicioList)
async def get_servicios(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    db: Session = Depends(get_db)
):
    """Obtener lista de servicios con paginación y búsqueda"""
    query = db.query(Servicio).filter(Servicio.deleted_at == None)
    
    # Aplicar búsqueda si se proporciona
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Servicio.nombre.ilike(search_filter)) |
            (Servicio.descripcion.ilike(search_filter))
        )
    
    # Obtener total de registros
    total = query.count()
    
    # Aplicar paginación
    servicios = query.order_by(Servicio.created_at.desc()).offset(skip).limit(limit).all()
    
    return ServicioList(
        items=[ServicioResponse.from_orm(s) for s in servicios],
        total=total
    )

@router.get("/{servicio_id}", response_model=ServicioResponse)
async def get_servicio(
    servicio_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un servicio por ID"""
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id, Servicio.deleted_at == None).first()
    
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado"
        )
    
    return ServicioResponse.from_orm(servicio)

@router.post("/", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
async def create_servicio(
    servicio_data: ServicioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Crear nuevo servicio (solo administradores)"""
    # Crear nuevo servicio
    db_servicio = Servicio(
        nombre=servicio_data.nombre,
        descripcion=servicio_data.descripcion,
        imagen=servicio_data.imagen or "/placeholder.jpg"
    )
    
    db.add(db_servicio)
    db.commit()
    db.refresh(db_servicio)
    
    return ServicioResponse.from_orm(db_servicio)

@router.put("/{servicio_id}", response_model=ServicioResponse)
async def update_servicio(
    servicio_id: int,
    servicio_data: ServicioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Actualizar servicio existente (solo administradores)"""
    # Buscar servicio
    db_servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    
    if not db_servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado"
        )
    
    # Actualizar campos
    update_data = servicio_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_servicio, field, value)
    
    db.commit()
    db.refresh(db_servicio)
    
    return ServicioResponse.from_orm(db_servicio)

@router.delete("/{servicio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_servicio(
    servicio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Eliminar servicio (solo administradores) - Soft delete"""
    # Buscar servicio
    db_servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    
    if not db_servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado"
        )
    
    # Soft delete: establecer deleted_at con la fecha actual
    db_servicio.deleted_at = datetime.utcnow()
    db.commit()
    
    return None
