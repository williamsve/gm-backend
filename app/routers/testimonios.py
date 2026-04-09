from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import uuid
from ..database import get_db
from ..models.testimonio import Testimonio, InvitacionTestimonio
from ..models.user import User
from ..schemas.testimonio import (
    TestimonioCreate, TestimonioUpdate, TestimonioResponse, TestimonioList,
    InvitacionCreate, InvitacionResponse, InvitacionList
)
from ..utils.auth import get_current_admin_user

router = APIRouter(prefix="/api/testimonios", tags=["Testimonios"])

@router.get("/", response_model=TestimonioList)
async def get_testimonios(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    search: Optional[str] = Query(None, description="Buscar por nombre o testimonio"),
    aprobado: Optional[bool] = Query(None, description="Filtrar por estado de aprobación"),
    db: Session = Depends(get_db)
):
    """Obtener lista de testimonios con paginación y búsqueda"""
    query = db.query(Testimonio).filter(Testimonio.is_active == True)
    
    # Filtrar por estado de aprobación si se proporciona
    if aprobado is not None:
        query = query.filter(Testimonio.is_approved == aprobado)
    
    # Aplicar búsqueda si se proporciona
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Testimonio.nombre.ilike(search_filter)) |
            (Testimonio.testimonio.ilike(search_filter))
        )
    
    # Obtener total de registros
    total = query.count()
    
    # Aplicar paginación
    testimonios = query.order_by(Testimonio.created_at.desc()).offset(skip).limit(limit).all()
    
    return TestimonioList(
        items=[TestimonioResponse.model_validate(t) for t in testimonios],
        total=total
    )

@router.post("/invitacion/{token}", response_model=TestimonioResponse, status_code=status.HTTP_201_CREATED)
async def create_testimonio_with_token(
    token: str,
    testimonio_data: TestimonioCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo testimonio usando token de invitación (público)"""
    # Validar que el token no esté vacío
    if not token or len(token) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de invitación inválido"
        )
    
    # Buscar la invitación en la base de datos
    invitacion = db.query(InvitacionTestimonio).filter(InvitacionTestimonio.token == token).first()
    
    # Verificar que el token existe
    if not invitacion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de invitación inválido o no existe"
        )
    
    # Verificar que el token no ha sido usado
    if invitacion.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token de invitación ya ha sido usado"
        )
    
    # Verificar que el token no ha expirado
    if invitacion.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token de invitación ha expirado"
        )
    
    # Crear testimonio
    db_testimonio = Testimonio(**testimonio_data.dict())
    
    db.add(db_testimonio)
    
    # Marcar la invitación como usada
    invitacion.used = True
    invitacion.used_at = datetime.now()
    
    db.commit()
    db.refresh(db_testimonio)
    
    return TestimonioResponse.model_validate(db_testimonio)


# Endpoints para gestión de invitaciones (solo administradores)
@router.get("/invitaciones", response_model=InvitacionList)
async def get_invitaciones(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Obtener lista de invitaciones de testimonios (solo administradores)"""
    query = db.query(InvitacionTestimonio).order_by(InvitacionTestimonio.created_at.desc())
    total = query.count()
    invitaciones = query.offset(skip).limit(limit).all()
    
    return InvitacionList(
        items=[InvitacionResponse.model_validate(i) for i in invitaciones],
        total=total
    )


@router.post("/invitaciones", response_model=InvitacionResponse, status_code=status.HTTP_201_CREATED)
async def create_invitacion(
    invitacion_data: InvitacionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Crear nueva invitación de testimonio (solo administradores)"""
    # Generar token único
    token = str(uuid.uuid4())
    
    # Calcular fecha de expiración
    expires_at = datetime.now() + timedelta(days=invitacion_data.expires_days)
    
    # Crear invitación
    db_invitacion = InvitacionTestimonio(
        token=token,
        email=invitacion_data.email,
        nombre=invitacion_data.nombre,
        expires_at=expires_at
    )
    
    db.add(db_invitacion)
    db.commit()
    db.refresh(db_invitacion)
    
    return InvitacionResponse.model_validate(db_invitacion)

@router.get("/{testimonio_id}", response_model=TestimonioResponse)
async def get_testimonio(
    testimonio_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un testimonio por ID"""
    testimonio = db.query(Testimonio).filter(Testimonio.id == testimonio_id, Testimonio.is_active == True).first()
    
    if not testimonio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Testimonio no encontrado"
        )
    
    return TestimonioResponse.model_validate(testimonio)

@router.post("/", response_model=TestimonioResponse, status_code=status.HTTP_201_CREATED)
async def create_testimonio(
    testimonio_data: TestimonioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Crear nuevo testimonio (solo administradores)"""
    db_testimonio = Testimonio(**testimonio_data.dict())
    
    db.add(db_testimonio)
    db.commit()
    db.refresh(db_testimonio)
    
    return TestimonioResponse.model_validate(db_testimonio)

@router.put("/{testimonio_id}", response_model=TestimonioResponse)
async def update_testimonio(
    testimonio_id: int,
    testimonio_data: TestimonioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Actualizar testimonio existente (solo administradores)"""
    db_testimonio = db.query(Testimonio).filter(Testimonio.id == testimonio_id).first()
    
    if not db_testimonio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Testimonio no encontrado"
        )
    
    # Actualizar campos
    update_data = testimonio_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_testimonio, field, value)
    
    db.commit()
    db.refresh(db_testimonio)
    
    return TestimonioResponse.from_orm(db_testimonio)

@router.delete("/{testimonio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_testimonio(
    testimonio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Eliminar testimonio (solo administradores)"""
    db_testimonio = db.query(Testimonio).filter(Testimonio.id == testimonio_id).first()
    
    if not db_testimonio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Testimonio no encontrado"
        )
    
    # Soft delete
    db_testimonio.is_active = False
    db.commit()
    
    return None
