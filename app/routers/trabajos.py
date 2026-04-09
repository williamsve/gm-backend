from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..database import get_db
from ..models.trabajo import Trabajo
from ..models.user import User
from ..schemas.trabajo import TrabajoCreate, TrabajoUpdate, TrabajoResponse, TrabajoList
from ..utils.auth import get_current_admin_user

router = APIRouter(prefix="/api/trabajos", tags=["Trabajos"])

@router.get("/", response_model=TrabajoList)
async def get_trabajos(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    db: Session = Depends(get_db)
):
    """Obtener lista de trabajos con paginación y búsqueda"""
    query = db.query(Trabajo).filter(Trabajo.is_active == True, Trabajo.deleted_at == None)
    
    # Aplicar búsqueda si se proporciona
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Trabajo.nombre.ilike(search_filter)) |
            (Trabajo.descripcion.ilike(search_filter))
        )
    
    # Obtener total de registros
    total = query.count()
    
    # Aplicar paginación
    trabajos = query.order_by(Trabajo.created_at.desc()).offset(skip).limit(limit).all()
    
    return TrabajoList(
        items=[TrabajoResponse.from_orm(t) for t in trabajos],
        total=total
    )

@router.get("/{trabajo_id}", response_model=TrabajoResponse)
async def get_trabajo(
    trabajo_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un trabajo por ID"""
    trabajo = db.query(Trabajo).filter(Trabajo.id == trabajo_id, Trabajo.is_active == True, Trabajo.deleted_at == None).first()
    
    if not trabajo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trabajo no encontrado"
        )
    
    return TrabajoResponse.from_orm(trabajo)

@router.post("/", response_model=TrabajoResponse, status_code=status.HTTP_201_CREATED)
async def create_trabajo(
    trabajo_data: TrabajoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Crear nuevo trabajo (solo administradores)"""
    db_trabajo = Trabajo(**trabajo_data.dict())
    
    db.add(db_trabajo)
    db.commit()
    db.refresh(db_trabajo)
    
    return TrabajoResponse.from_orm(db_trabajo)

@router.put("/{trabajo_id}", response_model=TrabajoResponse)
async def update_trabajo(
    trabajo_id: int,
    trabajo_data: TrabajoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Actualizar trabajo existente (solo administradores)"""
    db_trabajo = db.query(Trabajo).filter(Trabajo.id == trabajo_id).first()
    
    if not db_trabajo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trabajo no encontrado"
        )
    
    # Actualizar campos
    update_data = trabajo_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_trabajo, field, value)
    
    db.commit()
    db.refresh(db_trabajo)
    
    return TrabajoResponse.from_orm(db_trabajo)

@router.delete("/{trabajo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trabajo(
    trabajo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Eliminar trabajo (solo administradores) - Soft delete"""
    db_trabajo = db.query(Trabajo).filter(Trabajo.id == trabajo_id).first()
    
    if not db_trabajo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trabajo no encontrado"
        )
    
    # Soft delete: establecer deleted_at con la fecha actual
    db_trabajo.deleted_at = datetime.utcnow()
    db.commit()
    
    return None
