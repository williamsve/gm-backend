from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse, Token, UserLogin, RefreshTokenRequest, TokenRefreshResponse
from ..utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    add_token_to_blacklist,
    get_current_user,
    get_current_admin_user,
    create_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
    revoke_all_user_refresh_tokens
)
from ..config import get_settings

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

# Nombre de la cookie
TOKEN_COOKIE_NAME = "auth_token"

# OAuth2 scheme para obtener el token del header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Iniciar sesión y obtener token JWT"""
    # Buscar usuario
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar contraseña
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar si está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    # Obtener información del dispositivo
    device_info = request.headers.get("User-Agent", "Unknown")
    
    # Crear refresh token
    refresh_token = create_refresh_token(
        user_id=user.id,
        db=db,
        device_info=device_info
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user),
        "refresh_token": refresh_token
    }

@router.post("/login/json", response_model=Token)
@limiter.limit("5/minute")
async def login_json(
    request: Request,
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Iniciar sesión con JSON (alternativa a form-data)"""
    # Buscar usuario
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Verificar contraseña
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Verificar si está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    # Obtener información del dispositivo
    device_info = request.headers.get("User-Agent", "Unknown")
    
    # Crear refresh token
    refresh_token = create_refresh_token(
        user_id=user.id,
        db=db,
        device_info=device_info
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user),
        "refresh_token": refresh_token
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Obtener información del usuario actual"""
    return UserResponse.from_orm(current_user)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Registrar nuevo usuario (solo administradores)"""
    # Verificar si el username ya existe
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso"
        )
    
    # Verificar si el email ya existe (si se proporciona)
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso"
            )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.from_orm(db_user)

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Cerrar sesión e invalidar el token.
    
    El token se agrega a la blacklist para evitar que pueda ser usado
    después del logout, incluso si el token no ha expirado.
    """
    # Obtener el token del header Authorization
    auth_header = request.headers.get("Authorization")
    
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
    
    # Si hay un token válido, agregarlo a la blacklist
    if token:
        # Decodificar el token para obtener el jti y el usuario
        payload = verify_token(token, db)
        
        if payload:
            jti = payload.get("jti")
            username = payload.get("sub")
            
            # Buscar el usuario para obtener su ID
            if username and jti:
                user = db.query(User).filter(User.username == username).first()
                if user:
                    # Agregar el token a la blacklist
                    add_token_to_blacklist(jti=jti, user_id=user.id, db=db)
    
    # Limpiar la cookie
    response.delete_cookie(
        TOKEN_COOKIE_NAME,
        path="/",
        samesite="strict"
    )
    
    return {"message": "Sesión cerrada correctamente"}


@router.post("/set-cookie")
async def set_token_cookie(
    response: Response,
    token_data: dict
):
    """
    Endpoint para establecer la cookie HttpOnly con el token JWT.
    
    El frontend llama a este endpoint después del login para configurar
    la cookie de manera segura.
    
    Args:
        token_data: {"token": "el_token_jwt"}
    
    Returns:
        {"success": true, "message": "Cookie configurada"}
    """
    token = token_data.get("token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token no proporcionado"
        )
    
    # Calcular la duración de la cookie basada en la configuración del token
    # La cookie durará lo mismo que el token (24 horas por defecto)
    max_age = settings.access_token_expire_minutes * 60  # Convertir a segundos
    
    # Configurar la cookie
    # HttpOnly=True: No accesible desde JavaScript (protección XSS)
    # Secure=True: Solo envíala sobre HTTPS (en producción)
    # SameSite=Strict: Protege contra CSRF
    # Path=/: Disponible en toda la aplicación
    response.set_cookie(
        key=TOKEN_COOKIE_NAME,
        value=token,
        max_age=max_age,
        path="/",
        samesite="strict",
        httponly=True,
        secure=not settings.debug  # Solo Secure en producción
    )
    
    return {
        "success": True,
        "message": "Cookie configurada correctamente"
    }


@router.post("/cleanup-blacklist")
async def cleanup_blacklist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Endpoint para limpiar tokens blacklistados expirados.
    
    Solo los administradores pueden ejecutar esta limpieza.
    
    Returns:
        {"deleted_count": N} - número de tokens eliminados
    """
    from ..utils.auth import cleanup_expired_blacklist_tokens
    
    deleted_count = cleanup_expired_blacklist_tokens(db, days_old=7)
    
    return {
        "message": f"Limpieza completada",
        "deleted_count": deleted_count
    }


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para refrescar el access token usando un refresh token.
    
    Este endpoint permite obtener un nuevo access token sin necesidad de
    volver a iniciar sesión. El refresh token se invalida y se genera uno nuevo
    (rotación de tokens) por seguridad.
    
    Args:
        refresh_data: Contiene el refresh_token
    
    Returns:
        Nuevo access_token y refresh_token
    """
    # Verificar el refresh token
    refresh_token_obj = verify_refresh_token(refresh_data.refresh_token, db)
    
    if not refresh_token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado"
        )
    
    # Obtener el usuario
    user = db.query(User).filter(User.id == refresh_token_obj.user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo"
        )
    
    # Revocar el refresh token antiguo (rotación de tokens)
    revoke_refresh_token(refresh_data.refresh_token, db)
    
    # Crear nuevo access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    # Crear nuevo refresh token
    device_info = request.headers.get("User-Agent", "Unknown")
    new_refresh_token = create_refresh_token(
        user_id=user.id,
        db=db,
        device_info=device_info
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/revoke-refresh")
async def revoke_refresh_token_endpoint(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revocar un refresh token específico.
    
    Args:
        refresh_data: Contiene el refresh_token a revocar
    
    Returns:
        Mensaje de éxito
    """
    # Verificar que el token pertenezca al usuario
    refresh_token_obj = verify_refresh_token(refresh_data.refresh_token, db)
    
    if not refresh_token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado"
        )
    
    if refresh_token_obj.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para revocar este token"
        )
    
    # Revocar el token
    revoke_refresh_token(refresh_data.refresh_token, db)
    
    return {"message": "Refresh token revocado correctamente"}


@router.post("/revoke-all-sessions")
async def revoke_all_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revocar todos los refresh tokens del usuario (cerrar todas las sesiones).
    
    Returns:
        Número de sesiones cerradas
    """
    revoked_count = revoke_all_user_refresh_tokens(current_user.id, db)
    
    return {
        "message": f"Se han cerrado {revoked_count} sesiones",
        "revoked_count": revoked_count
    }
