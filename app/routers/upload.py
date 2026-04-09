from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from pathlib import Path

from ..database import get_db
from ..models.user import User
from ..utils.auth import get_current_admin_user

router = APIRouter(prefix="/api/upload", tags=["Upload"])

# Directorio base donde se guardarán las imágenes
BASE_UPLOAD_DIR = Path("public/uploads")
BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/imagenes", response_model=dict)
async def upload_imagenes(
    files: List[UploadFile] = File(...),
    tipo: str = Query("trabajos", description="Tipo de upload: trabajos o servicios"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Subir múltiples imágenes para trabajos o servicios"""
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden subir más de 10 imágenes a la vez"
        )
    
    # Validar tipo de upload
    if tipo not in ["trabajos", "servicios"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de upload inválido. Use 'trabajos' o 'servicios'"
        )
    
    # Crear directorio si no existe
    upload_dir = BASE_UPLOAD_DIR / tipo
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    urls = []
    
    for file in files:
        # Validar tipo de archivo
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo {file.filename} no es una imagen válida"
            )
        
        # Validar tamaño (máximo 5MB)
        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo {file.filename} excede el tamaño máximo de 5MB"
            )
        
        # Generar nombre único para el archivo
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Guardar archivo
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        # Generar URL relativa
        url = f"/uploads/{tipo}/{unique_filename}"
        urls.append(url)
    
    return {"urls": urls, "message": f"Se subieron {len(urls)} imágenes correctamente"}
