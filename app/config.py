import os
import json
import secrets
from pydantic_settings import BaseSettings
from functools import lru_cache


def generate_secret_key() -> str:
    """Genera una clave secreta segura para desarrollo local."""
    return secrets.token_urlsafe(32)


class Settings(BaseSettings):
    # Configuración de la aplicación
    app_name: str = "Global Mantenimiento API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Seguridad
    # Lee SECRET_KEY desde variables de entorno, genera una segura solo para desarrollo
    secret_key: str = generate_secret_key()
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 horas
    refresh_token_expire_days: int = 7  # 7 días para refresh token
    
    # Base de datos
    # Lee DATABASE_URL desde variables de entorno
    database_url: str = ""
    
    # CORS
    # Lee ALLOWED_ORIGINS desde variables de entorno (formato JSON array)
    # Valor por defecto incluye localhost:3000 y localhost:3001 para desarrollo
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Servidor
    host: str = "0.0.0.0"
    port: int = 8000
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parsear ALLOWED_ORIGINS si viene como string JSON
        if isinstance(self.allowed_origins, str):
            try:
                self.allowed_origins = json.loads(self.allowed_origins)
            except:
                self.allowed_origins = [self.allowed_origins]
        
        # Leer PORT desde el entorno en tiempo de instanciación, no de definición de clase
        if "PORT" in os.environ:
            self.port = int(os.environ["PORT"])
        
        # Validar que DATABASE_URL esté configurado en producción
        if not self.database_url and not self.debug:
            raise ValueError("DATABASE_URL es requerido en producción")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()
