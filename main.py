from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import engine, Base
from app.routers import auth_router, servicios_router, proyectos_router, testimonios_router, trabajos_router, visitas_router, upload_router, configuracion_router
from app.utils.auth import get_password_hash
from app.models.user import User
from app.database import SessionLocal

# Configurar limiter usando IP del cliente (considerando proxy)
limiter = Limiter(key_func=get_remote_address)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Crear tablas en la base de datos
    Base.metadata.create_all(bind=engine)
    
    # Crear usuario administrador por defecto si no existe
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            hashed_password = get_password_hash("admin123"[:72])
            admin_user = User(
                username="admin",
                email="admin@globalmantenimiento.site",
                hashed_password=hashed_password,
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            print("Usuario administrador por defecto creado")
    except Exception as e:
        print(f"Error al crear usuario admin: {e}")
    finally:
        db.close()
    
    yield
    
    # Cleanup al apagar
    print("Aplicación FastAPI detenida")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API REST para Global Mantenimiento C.A.",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Agregar el limiter al estado de la app
app.state.limiter = limiter

# Manejador de excepciones para RateLimitExceeded
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Manejar excepciones cuando se excede el límite de requests"""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Has excedido el límite de solicitudes",
            "message": f"Por favor, espera {exc.detail} antes de intentar de nuevo",
            "retry_after": exc.detail
        }
    )

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router)
app.include_router(servicios_router)
app.include_router(proyectos_router)
app.include_router(testimonios_router)
app.include_router(trabajos_router)
app.include_router(visitas_router)
app.include_router(upload_router)
app.include_router(configuracion_router)

# Servir archivos estáticos desde el directorio public
app.mount("/uploads", StaticFiles(directory="public/uploads"), name="uploads")

@app.get("/", tags=["Root"])
@limiter.limit("100/minute")
async def root(request: Request):
    """Endpoint raíz de la API"""
    return {
        "message": "Bienvenido a la API de Global Mantenimiento",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["Health"])
@limiter.limit("100/minute")
async def health_check(request: Request):
    """Verificar estado de la API"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
