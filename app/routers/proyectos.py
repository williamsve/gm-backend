from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..database import get_db
from ..models.proyecto import Proyecto
from ..models.user import User
from ..schemas.proyecto import ProyectoCreate, ProyectoUpdate, ProyectoResponse, ProyectoList
from ..utils.auth import get_current_admin_user

router = APIRouter(prefix="/api/proyectos", tags=["Proyectos"])

@router.get("/", response_model=ProyectoList)
async def get_proyectos(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    db: Session = Depends(get_db)
):
    """Obtener lista de proyectos con paginación y búsqueda"""
    query = db.query(Proyecto).filter(Proyecto.is_active == True, Proyecto.deleted_at == None)
    
    # Aplicar búsqueda si se proporciona
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Proyecto.nombre.ilike(search_filter)) |
            (Proyecto.descripcion.ilike(search_filter))
        )
    
    # Obtener total de registros
    total = query.count()
    
    # Aplicar paginación
    proyectos = query.order_by(Proyecto.created_at.desc()).offset(skip).limit(limit).all()
    
    return ProyectoList(
        items=[ProyectoResponse.from_orm(p) for p in proyectos],
        total=total
    )

@router.get("/{proyecto_id}", response_model=ProyectoResponse)
async def get_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un proyecto por ID"""
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id, Proyecto.is_active == True, Proyecto.deleted_at == None).first()
    
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    return ProyectoResponse.from_orm(proyecto)

@router.post("/", response_model=ProyectoResponse, status_code=status.HTTP_201_CREATED)
async def create_proyecto(
    proyecto_data: ProyectoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Crear nuevo proyecto (solo administradores)"""
    db_proyecto = Proyecto(**proyecto_data.dict())
    
    db.add(db_proyecto)
    db.commit()
    db.refresh(db_proyecto)
    
    return ProyectoResponse.from_orm(db_proyecto)

@router.put("/{proyecto_id}", response_model=ProyectoResponse)
async def update_proyecto(
    proyecto_id: int,
    proyecto_data: ProyectoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Actualizar proyecto existente (solo administradores)"""
    db_proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    
    if not db_proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Actualizar campos
    update_data = proyecto_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_proyecto, field, value)
    
    db.commit()
    db.refresh(db_proyecto)
    
    return ProyectoResponse.from_orm(db_proyecto)

@router.delete("/{proyecto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Eliminar proyecto (solo administradores) - Soft delete"""
    db_proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    
    if not db_proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Soft delete: establecer deleted_at con la fecha actual
    db_proyecto.deleted_at = datetime.utcnow()
    db.commit()
    
    return None
