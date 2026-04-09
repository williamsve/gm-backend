"""
Migración para crear la tabla token_blacklist.

Esta tabla almacena los tokens JWT que han sido invalidados (por logout),
permitiendo validar que un token ha sido revocado aunque todavía no haya expirado.
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


def create_token_blacklist_table():
    """Crea la tabla token_blacklist."""
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
                WHERE table_name = 'token_blacklist'
            )
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("La tabla 'token_blacklist' ya existe, omitiendo.")
        else:
            # Crear la tabla
            cursor.execute("""
                CREATE TABLE token_blacklist (
                    id SERIAL PRIMARY KEY,
                    jti VARCHAR(36) NOT NULL UNIQUE,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    token_type VARCHAR(20) DEFAULT 'access',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Crear índice para búsquedas rápidas por jti
            cursor.execute("""
                CREATE INDEX idx_token_blacklist_jti 
                ON token_blacklist(jti)
            """)
            
            # Crear índice para búsquedas por user_id
            cursor.execute("""
                CREATE INDEX idx_token_blacklist_user_id 
                ON token_blacklist(user_id)
            """)
            
            print("Tabla 'token_blacklist' creada exitosamente")
            print("Índices creados: idx_token_blacklist_jti, idx_token_blacklist_user_id")
        
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
    success = create_token_blacklist_table()
    exit(0 if success else 1)