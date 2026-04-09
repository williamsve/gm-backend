"""
Migracion para cambiar la columna 'imagen' a 'imagenes' en la tabla trabajos.
Este script:
1. Renombra la columna 'imagen' a 'imagenes'
2. Cambia el tipo de dato de String a JSON
3. Convierte los datos existentes de string a array
"""

import sys
import os
import json

# Agregar el directorio raiz al path para importar modulos de la app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

def run_migration():
    """Ejecutar la migracion para cambiar imagen a imagenes"""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    print("Iniciando migracion: imagen -> imagenes")
    print("=" * 50)
    
    with engine.connect() as conn:
        # Verificar si la columna 'imagen' existe
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('trabajos')]
        
        if 'imagen' not in columns:
            print("[ERROR] La columna 'imagen' no existe en la tabla 'trabajos'")
            print(f"Columnas existentes: {columns}")
            return False
        
        if 'imagenes' in columns:
            print("[ADVERTENCIA] La columna 'imagenes' ya existe en la tabla 'trabajos'")
            print("No se requiere migracion")
            return True
        
        print("[OK] Columna 'imagen' encontrada")
        print("[OK] Columna 'imagenes' no existe (procediendo con migracion)")
        
        try:
            # Paso 1: Agregar nueva columna JSON
            print("\nPaso 1: Agregando columna 'imagenes' (JSON)...")
            conn.execute(text(
                "ALTER TABLE trabajos ADD COLUMN imagenes JSON DEFAULT '[]'::json"
            ))
            conn.commit()
            print("[OK] Columna 'imagenes' agregada")
            
            # Paso 2: Migrar datos existentes
            print("\nPaso 2: Migrando datos existentes...")
            result = conn.execute(text(
                "SELECT id, imagen FROM trabajos WHERE imagen IS NOT NULL AND imagen != ''"
            ))
            rows = result.fetchall()
            
            migrated_count = 0
            for row in rows:
                trabajo_id = row[0]
                imagen_value = row[1]
                
                # Convertir string a array JSON
                if imagen_value:
                    # Si ya es un JSON valido, parsearlo
                    try:
                        imagenes_array = json.loads(imagen_value)
                        if not isinstance(imagenes_array, list):
                            imagenes_array = [imagen_value]
                    except (json.JSONDecodeError, TypeError):
                        # Si no es JSON, tratarlo como URL simple
                        imagenes_array = [imagen_value]
                    
                    # Actualizar la nueva columna
                    conn.execute(
                        text("UPDATE trabajos SET imagenes = :imagenes WHERE id = :id"),
                        {"imagenes": json.dumps(imagenes_array), "id": trabajo_id}
                    )
                    migrated_count += 1
            
            conn.commit()
            print(f"[OK] {migrated_count} registros migrados")
            
            # Paso 3: Eliminar columna antigua
            print("\nPaso 3: Eliminando columna 'imagen' antigua...")
            conn.execute(text("ALTER TABLE trabajos DROP COLUMN imagen"))
            conn.commit()
            print("[OK] Columna 'imagen' eliminada")
            
            print("\n" + "=" * 50)
            print("[EXITO] Migracion completada exitosamente!")
            print(f"   - Columna 'imagen' renombrada a 'imagenes'")
            print(f"   - Tipo de dato cambiado a JSON")
            print(f"   - {migrated_count} registros migrados")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Error durante la migracion: {e}")
            conn.rollback()
            return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
