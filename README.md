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

### Configurar variables de entorno

Editar el archivo `.env` con tus credenciales:

```env
SECRET_KEY=tu-secreto-seguro
DATABASE_URL=postgresql://usuario:password@host:puerto/database
ALLOWED_ORIGINS=http://localhost:3000
```

## 🏃‍♂️ Ejecutar

### Desarrollo

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Producción

```bash
cd api
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📚 Documentación

Una vez ejecutando la API, acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 Autenticación

### Credenciales por defecto

- **Usuario**: `admin`
- **Contraseña**: `admin123`

### Obtener token

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Usar token

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
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

## 🔌 Endpoints

### Autenticación

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login` | Iniciar sesión (form-data) | ❌ |
| POST | `/api/auth/login/json` | Iniciar sesión (JSON) | ❌ |
| GET | `/api/auth/me` | Obtener usuario actual | ✅ |
| POST | `/api/auth/register` | Registrar usuario | ✅ Admin |
| POST | `/api/auth/logout` | Cerrar sesión | ❌ |

### Servicios

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/servicios/` | Listar servicios | ❌ |
| GET | `/api/servicios/{id}` | Obtener servicio | ❌ |
| POST | `/api/servicios/` | Crear servicio | ✅ Admin |
| PUT | `/api/servicios/{id}` | Actualizar servicio | ✅ Admin |
| DELETE | `/api/servicios/{id}` | Eliminar servicio | ✅ Admin |

### Query Parameters (GET /api/servicios/)

- `skip`: Número de registros a saltar (default: 0)
- `limit`: Número máximo de registros (default: 100, max: 1000)
- `search`: Buscar por nombre o descripción

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
