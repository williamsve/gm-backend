from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación con tokens blacklistados
    blacklisted_tokens = relationship("TokenBlacklist", back_populates="user", cascade="all, delete-orphan")
    
    # Relación con refresh tokens
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


class TokenBlacklist(Base):
    """
    Tabla para almacenar tokens JWT invalidados (logout).
    Almacenamos solo el jti (identificador único del token) en lugar del token completo
    para optimizar espacio.
    """
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(36), unique=True, index=True, nullable=False)  # JWT ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_type = Column(String(20), default="access")  # tipo de token
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación con usuario
    user = relationship("User", back_populates="blacklisted_tokens")
    
    def __repr__(self):
        return f"<TokenBlacklist(jti={self.jti}, user_id={self.user_id})>"


class RefreshToken(Base):
    """
    Tabla para almacenar refresh tokens.
    
    Los refresh tokens permiten obtener un nuevo access token sin necesidad
    de volver a iniciar sesión. Tienen una vigencia más larga que los access tokens.
    """
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)  # Refresh token único
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Cuándo expira
    revoked = Column(Boolean, default=False)  # Si ha sido revocado
    revoked_at = Column(DateTime(timezone=True), nullable=True)  # Cuándo fue revocado
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    device_info = Column(String(255), nullable=True)  # Información del dispositivo
    
    # Relación con usuario
    user = relationship("User", back_populates="refresh_tokens")
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.revoked})>"
