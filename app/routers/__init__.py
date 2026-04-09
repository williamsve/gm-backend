from .auth import router as auth_router
from .servicios import router as servicios_router
from .proyectos import router as proyectos_router
from .testimonios import router as testimonios_router
from .trabajos import router as trabajos_router
from .visitas import router as visitas_router
from .upload import router as upload_router
from .configuracion import router as configuracion_router

__all__ = ["auth_router", "servicios_router", "proyectos_router", "testimonios_router", "trabajos_router", "visitas_router", "upload_router", "configuracion_router"]
