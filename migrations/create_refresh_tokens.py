"""
Migración para crear la tabla refresh_tokens.

Esta tabla almacena los refresh tokens que permiten obtener un nuevo
access token sin necesidad de volver a iniciar sesión.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Agregar el directorio raíz al path para importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno desde la raíz del proyecto
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env.local'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


def get_database_url():
    """Obtiene la URL de la base de datos desde las variables de entorno."""
    # Primero intentar con DATABASE_URL_UNPOOLED
    db_url = os.getenv('DATABASE_URL_UNPOOLED') or os.getenv('DATABASE_URL')
    
    # Si no hay URL de neon, construir desde variables individuales
    if not db_url:
        pg_host = os.getenv('PGHOST_UNPOOLED') or os.getenv('PGHOST')
        pg_user = os.getenv('PGUSER') or os.getenv('POSTGRES_USER')
        pg_password = os.getenv('PGPASSWORD') or os.getenv('POSTGRES_PASSWORD')
        pg_database = os.getenv('PGDATABASE') or os.getenv('POSTGRES_DATABASE')
        
        if pg_host and pg_user and pg_password and pg_database:
            db_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}/{pg_database}?sslmode=require"
    
    return db_url


def create_refresh_tokens_table():
    """Crea la tabla refresh_tokens."""
    database_url = get_database_url()
    
    if not database_url:
        print("ERROR: No se encontró la variable DATABASE_URL")
        return False
    
    print(f"Conectando a la base de datos...")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar si la tabla ya existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'refresh_tokens'
            )
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("La tabla 'refresh_tokens' ya existe, omitiendo.")
        else:
            # Crear la tabla
            cursor.execute("""
                CREATE TABLE refresh_tokens (
                    id SERIAL PRIMARY KEY,
                    token VARCHAR(255) NOT NULL UNIQUE,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    revoked BOOLEAN DEFAULT FALSE,
                    revoked_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    device_info VARCHAR(255)
                )
            """)
            
            # Crear índice para búsquedas rápidas por token
            cursor.execute("""
                CREATE INDEX idx_refresh_tokens_token 
                ON refresh_tokens(token)
            """)
            
            # Crear índice para búsquedas por user_id
            cursor.execute("""
                CREATE INDEX idx_refresh_tokens_user_id 
                ON refresh_tokens(user_id)
            """)
            
            # Crear índice para búsquedas por expires_at (para limpieza)
            cursor.execute("""
                CREATE INDEX idx_refresh_tokens_expires_at 
                ON refresh_tokens(expires_at)
            """)
            
            print("Tabla 'refresh_tokens' creada exitosamente")
            print("Índices creados: idx_refresh_tokens_token, idx_refresh_tokens_user_id, idx_refresh_tokens_expires_at")
        
        conn.commit()
        print("\n¡Migración completada exitosamente!")
        
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
    success = create_refresh_tokens_table()
    exit(0 if success else 1)