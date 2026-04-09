"""
Migración para agregar columnas deleted_at a las tablas de la base de datos.

Este script agrega la columna 'deleted_at' (TIMESTAMP, nullable) a las tablas:
- trabajos
- servicios
- proyectos
"""

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Cargar variables de entorno
# Primero cargar .env.local (raíz del proyecto), luego api/.env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

def get_database_url():
    """Obtiene la URL de la base de datos desde las variables de entorno."""
    # Usar la URL sin pooling para evitar problemas de pgBouncer
    return os.getenv('DATABASE_URL_UNPOOLED') or os.getenv('DATABASE_URL')

def add_deleted_at_columns():
    """Agrega las columnas deleted_at a las tablas requeridas."""
    database_url = get_database_url()
    
    if not database_url:
        print("ERROR: No se encontró la variable DATABASE_URL")
        return False
    
    print(f"Conectando a la base de datos...")
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Tablas a modificar
        tables = ['trabajos', 'servicios', 'proyectos']
        
        for table_name in tables:
            print(f"Procesando tabla: {table_name}")
            
            # Verificar si la columna ya existe
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name = 'deleted_at'
            """, (table_name,))
            
            exists = cursor.fetchone()
            
            if exists:
                print(f"  - La columna 'deleted_at' ya existe en '{table_name}', omitiendo.")
            else:
                # Agregar la columna
                cursor.execute(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE NULL
                """)
                print(f"  - Columna 'deleted_at' agregada exitosamente a '{table_name}'")
        
        # Confirmar los cambios
        conn.commit()
        print("\n¡Migración completada exitosamente!")
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"ERROR de base de datos: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = add_deleted_at_columns()
    exit(0 if success else 1)