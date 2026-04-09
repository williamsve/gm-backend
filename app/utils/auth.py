from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..config import get_settings
from ..database import get_db
from ..models.user import User, TokenBlacklist, RefreshToken

settings = get_settings()

# Configurar OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña plana contra hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Generar hash de contraseña"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

import uuid

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear token JWT de acceso.
    
    El token incluye un 'jti' (JWT ID) único que se usa para identificar
    el token en la blacklist.
    """
    to_encode = data.copy()
    
    # Agregar JTI único para identificar el token
    if "jti" not in to_encode:
        to_encode["jti"] = str(uuid.uuid4())
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str, db: Session = None) -> Optional[dict]:
    """
    Verificar y decodificar token JWT.
    
    Args:
        token: Token JWT a verificar
        db: Sesión de base de datos (opcional)
    
    Returns:
        Payload decodificado si el token es válido, None si no lo es
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Verificar si el token está en la blacklist
        if db is not None:
            jti = payload.get("jti")
            if jti:
                blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
                if blacklisted:
                    # Token revocado
                    return None
        
        return payload
    except JWTError:
        return None

def is_token_blacklisted(jti: str, db: Session) -> bool:
    """
    Verificar si un token está en la blacklist.
    
    Args:
        jti: Identificador único del token (JWT ID)
        db: Sesión de base de datos
    
    Returns:
        True si el token está en la blacklist, False si no
    """
    blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
    return blacklisted is not None

def add_token_to_blacklist(jti: str, user_id: int, db: Session, token_type: str = "access") -> bool:
    """
    Agregar un token a la blacklist (invalidar token).
    
    Args:
        jti: Identificador único del token (JWT ID)
        user_id: ID del usuario que hizo logout
        db: Sesión de base de datos
        token_type: Tipo de token (default: "access")
    
    Returns:
        True si se agregó correctamente
    """
    try:
        # Verificar si ya está en la blacklist
        existing = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
        if existing:
            return True  # Ya está invalidado
        
        blacklisted_token = TokenBlacklist(
            jti=jti,
            user_id=user_id,
            token_type=token_type
        )
        db.add(blacklisted_token)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False

def cleanup_expired_blacklist_tokens(db: Session, days_old: int = 7) -> int:
    """
    Limpiar tokens blacklistados que ya expiraron.
    
    Los tokens JWT tienen una fecha de expiración (exp). Los tokens blacklistados
    que ya expiraron pueden ser eliminados de la blacklist para mantener
    la tabla pequeños.
    
    Args:
        db: Sesión de base de datos
        days_old: Días después de la expiración para eliminar (default: 7)
    
    Returns:
        Número de tokens eliminados
    """
    from datetime import timezone
    
    # Calcular la fecha límite (ahora - days_old)
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
    
    # Eliminar tokens blacklistados anteriores a la fecha límite
    deleted = db.query(TokenBlacklist).filter(
        TokenBlacklist.created_at < cutoff_date
    ).delete()
    
    db.commit()
    return deleted

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Obtener usuario actual desde token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Pasar la sesión de DB para verificar la blacklist
    payload = verify_token(token, db)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Obtener usuario activo actual"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Obtener usuario administrador actual"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    return current_user


# ==================== Funciones de Refresh Token ====================

def create_refresh_token(user_id: int, db: Session, device_info: str = None) -> str:
    """
    Crear un nuevo refresh token y guardarlo en la base de datos.
    
    Args:
        user_id: ID del usuario
        db: Sesión de base de datos
        device_info: Información opcional del dispositivo
    
    Returns:
        El token refresh generado
    """
    import secrets
    
    # Generar un token único
    token = secrets.token_urlsafe(64)  # Token largo y seguro
    
    # Calcular fecha de expiración
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    # Crear el registro en la base de datos
    refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at,
        device_info=device_info
    )
    
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    
    return token


def verify_refresh_token(token: str, db: Session) -> Optional[RefreshToken]:
    """
    Verificar un refresh token.
    
    Args:
        token: El refresh token a verificar
        db: Sesión de base de datos
    
    Returns:
        El objeto RefreshToken si es válido, None si no lo es
    """
    # Buscar el token en la base de datos
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == token
    ).first()
    
    if not refresh_token:
        return None
    
    # Verificar si está revocado
    if refresh_token.revoked:
        return None
    
    # Verificar si ha expirado
    if refresh_token.expires_at < datetime.utcnow():
        return None
    
    return refresh_token


def revoke_refresh_token(token: str, db: Session) -> bool:
    """
    Revocar un refresh token.
    
    Args:
        token: El refresh token a revocar
        db: Sesión de base de datos
    
    Returns:
        True si se revocó correctamente, False si no se encontró
    """
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == token
    ).first()
    
    if not refresh_token:
        return False
    
    refresh_token.revoked = True
    refresh_token.revoked_at = datetime.utcnow()
    
    db.commit()
    return True


def revoke_all_user_refresh_tokens(user_id: int, db: Session) -> int:
    """
    Revocar todos los refresh tokens de un usuario (cerrar todas las sesiones).
    
    Args:
        user_id: ID del usuario
        db: Sesión de base de datos
    
    Returns:
        Número de tokens revocados
    """
    from datetime import timezone
    
    result = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked == False
    ).update({
        RefreshToken.revoked: True,
        RefreshToken.revoked_at: datetime.now(timezone.utc)
    })
    
    db.commit()
    return result


def cleanup_expired_refresh_tokens(db: Session) -> int:
    """
    Limpiar refresh tokens expirados de la base de datos.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Número de tokens eliminados
    """
    from datetime import timezone
    
    # Eliminar tokens expirados que ya están revocados
    deleted = db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.now(timezone.utc)
    ).delete()
    
    db.commit()
    return deleted
