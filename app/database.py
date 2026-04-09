from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()

# Crear engine de SQLAlchemy
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verificar conexiones antes de usar
    pool_size=5,  # Tamaño del pool de conexiones
    max_overflow=10  # Conexiones adicionales permitidas
)

# Crear sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Dependency para obtener sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
