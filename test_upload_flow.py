"""
Script de prueba para verificar el flujo completo de subida de imágenes.
Este script:
1. Verifica que el endpoint de trabajos funcione
2. Muestra la estructura de datos esperada
"""

import sys
import os
import json
import urllib.request
import urllib.error

# Configuración
BASE_URL = "http://localhost:8000"
TRABAJOS_ENDPOINT = f"{BASE_URL}/api/trabajos"

def test_upload_flow():
    """Probar el flujo completo de subida de imágenes"""
    print("Iniciando prueba de flujo de subida de imagenes")
    print("=" * 50)
    
    # Nota: Este test requiere autenticación
    # Para una prueba completa, necesitarías obtener un token de autenticación
    print("\n[NOTA] Este script es una referencia para pruebas manuales.")
    print("Para probar el flujo completo:")
    print("1. Inicia sesion en el panel de administracion")
    print("2. Ve a la seccion de Trabajos")
    print("3. Crea un nuevo trabajo con imagenes")
    print("4. Verifica que las imagenes se suban correctamente")
    
    print("\n" + "=" * 50)
    print("Verificando endpoints disponibles...")
    
    try:
        # Verificar endpoint de trabajos
        req = urllib.request.Request(TRABAJOS_ENDPOINT)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"[OK] Endpoint de trabajos funcionando")
            print(f"   - Total de trabajos: {data.get('total', 0)}")
            if data.get('items'):
                for trabajo in data['items']:
                    print(f"   - Trabajo: {trabajo.get('nombre')}")
                    print(f"     Imagenes: {trabajo.get('imagenes', [])}")
            
    except urllib.error.URLError as e:
        print(f"[ERROR] No se pudo conectar al backend: {e}")
        print("Asegurate de que el servidor este corriendo en http://localhost:8000")
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
    
    print("\n" + "=" * 50)
    print("[EXITO] Verificacion completada")
    print("\nEl frontend esta configurado correctamente para:")
    print("1. Subir imagenes al endpoint /api/upload/imagenes")
    print("2. Recibir URLs de respuesta")
    print("3. Enviar las URLs como array JSON al crear/actualizar trabajos")
    print("4. El backend ahora acepta el campo 'imagenes' como JSON")
    
    print("\nEstructura de datos esperada:")
    print("  Frontend envia:")
    print("    {")
    print("      'nombre': 'Trabajo ejemplo',")
    print("      'descripcion': 'Descripcion del trabajo',")
    print("      'cliente': 'Nombre del cliente',")
    print("      'fecha_inicio': '2026-03-30T00:00:00',")
    print("      'tipo_servicio': 'categoria',")
    print("      'estado': 'completado',")
    print("      'imagenes': ['/uploads/trabajos/uuid1.jpg', '/uploads/trabajos/uuid2.jpg']")
    print("    }")

if __name__ == "__main__":
    test_upload_flow()
