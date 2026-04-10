# API FastAPI - Global Mantenimiento

## 📋 Descripción

API REST construida con FastAPI para el sistema de Global Mantenimiento C.A.

## 🚀 Características

- ✅ **Autenticación JWT** con tokens de acceso
- ✅ **Validación automática** con Pydantic
- ✅ **Documentación automática** (Swagger UI y ReDoc)
- ✅ **CORS configurado** para frontend Next.js
- ✅ **Base de datos PostgreSQL** con SQLAlchemy
- ✅ **Endpoints protegidos** con roles de usuario
- ✅ **Paginación y búsqueda** en endpoints

## 📦 Instalación

### Requisitos previos
- Python 3.9+
- PostgreSQL (o usar la base de datos existente)

### Instalar dependencias

```bash
cd api
pip install -r requirements.txt
```


## 📁 Estructura del proyecto

```
api/
├── main.py                 # Punto de entrada de FastAPI
├── requirements.txt        # Dependencias de Python
├── .env                   # Variables de entorno
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuración de la aplicación
│   ├── database.py        # Configuración de SQLAlchemy
│   ├── models/            # Modelos de SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── servicio.py
│   ├── schemas/           # Esquemas Pydantic
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── servicio.py
│   ├── routers/           # Routers de endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── servicios.py
│   └── utils/             # Utilidades
│       ├── __init__.py
│       └── auth.py        # Utilidades de autenticación JWT
└── README.md
```

## 🔒 Seguridad

- **JWT**: Tokens con expiración de 24 horas
- **bcrypt**: Hash de contraseñas
- **CORS**: Configurado para frontend permitido
- **Roles**: Sistema de roles (admin, user)
- **Validación**: Automática con Pydantic

## 🧪 Testing

```bash
cd api
pytest
```

## 📝 Notas

- La API usa la misma base de datos que Next.js para compatibilidad
- El usuario admin se crea automáticamente al iniciar la aplicación
- Los endpoints protegidos requieren header `Authorization: Bearer TOKEN`
- La documentación se genera automáticamente desde el código

## 🔄 Migración desde Next.js

Esta API reemplaza los endpoints de Next.js en:
- `pages/api/auth/*`
- `pages/api/servicios/*`

El frontend Next.js debe actualizarse para usar esta API en:
- `http://localhost:8000` (desarrollo)
- URL de producción configurada en `.env`
