#!/usr/bin/env python3
"""
Script de inicialización de secrets para desarrollo local.

Este script genera una clave secreta segura y la guarda en el archivo .env
si no existe. Solo debe usarse en desarrollo local, NO en producción.

Usage:
    python init_secrets.py

El script generará automáticamente una clave segura usando secrets.token_urlsafe(32)
y la guardará en api/.env para desarrollo local.
"""

import os
import secrets
from pathlib import Path

# Determinar la ruta del archivo .env
SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / "api" / ".env"


def generate_secret_key() -> str:
    """Genera una clave secreta segura usando el módulo secrets."""
    return secrets.token_urlsafe(32)


def init_secrets():
    """Inicializa el archivo .env con una clave secreta segura si no existe."""
    
    if ENV_FILE.exists():
        # Verificar si ya existe SECRET_KEY
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if "SECRET_KEY=" in content:
                print(f"✓ El archivo {ENV_FILE} ya existe y tiene SECRET_KEY configurado.")
                print("  No se realizan cambios.")
                return
    
    # Generar nueva clave secreta
    secret_key = generate_secret_key()
    
    # Crear contenido del .env
    env_content = f"""# Configuración de la API FastAPI
# IMPORTANTE: Este archivo contiene secrets - NO commitear a repositorio
# Generado automáticamente por init_secrets.py

# Clave secreta para JWT (generada automáticamente)
SECRET_KEY={secret_key}

# Algoritmo de firma JWT
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Base de datos - configurar según el entorno
# Para desarrollo local: postgresql://user:password@localhost:5432/dbname
# Para producción: configurar en Vercel Environment Variables
DATABASE_URL=

# CORS (permitir requests desde Next.js)
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
DEBUG=true
"""
    
    # Escribir el archivo
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"✓ Archivo {ENV_FILE} creado exitosamente.")
    print(f"✓ SECRET_KEY generada: {secret_key[:20]}...")
    print("\nRecordatorio: Añade este archivo a .gitignore si no lo está.")
    print("Para producción, configura las variables en Vercel:")
    print("  - SECRET_KEY (requerido)")
    print("  - DATABASE_URL (requerido)")
    print("  - ALLOWED_ORIGINS (requerido)")


if __name__ == "__main__":
    init_secrets()