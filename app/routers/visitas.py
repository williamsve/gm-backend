from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import List, Optional
import json

from app.database import get_db
from app.models.visita import Visita
from app.schemas.visita import VisitaCreate, VisitaResponse, EstadisticasVisitas

router = APIRouter(prefix="/api/visitas", tags=["Visitas"])

@router.post("/", response_model=VisitaResponse)
def registrar_visita(visita: VisitaCreate, request: Request, db: Session = Depends(get_db)):
    """Registrar una nueva visita al sitio"""
    # Obtener IP del cliente
    client_ip = request.client.host if request.client else None
    
    # Crear nueva visita
    db_visita = Visita(
        ip_address=visita.ip_address or client_ip,
        user_agent=visita.user_agent,
        pagina=visita.pagina,
        pais=visita.pais,
        ciudad=visita.ciudad,
        region=visita.region,
        latitud=visita.latitud,
        longitud=visita.longitud
    )
    
    db.add(db_visita)
    db.commit()
    db.refresh(db_visita)
    
    return db_visita

@router.get("/estadisticas", response_model=EstadisticasVisitas)
def obtener_estadisticas(
    mes: Optional[int] = None,
    anio: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de visitas con filtro por mes"""
    query = db.query(Visita)
    
    # Aplicar filtro por mes y año si se especifica
    if mes and anio:
        query = query.filter(
            extract('month', Visita.fecha) == mes,
            extract('year', Visita.fecha) == anio
        )
    elif anio:
        query = query.filter(extract('year', Visita.fecha) == anio)
    
    # Total de visitas
    total_visitas = query.count()
    
    # Visitas por mes (últimos 12 meses)
    visitas_por_mes = {}
    for i in range(12):
        fecha = datetime.now() - timedelta(days=30*i)
        mes_num = fecha.month
        anio_num = fecha.year
        
        count = db.query(Visita).filter(
            extract('month', Visita.fecha) == mes_num,
            extract('year', Visita.fecha) == anio_num
        ).count()
        
        nombre_mes = fecha.strftime('%B %Y')
        visitas_por_mes[nombre_mes] = count
    
    # Visitas por país
    visitas_por_pais = {}
    paises = db.query(Visita.pais, func.count(Visita.id)).filter(
        Visita.pais.isnot(None)
    ).group_by(Visita.pais).all()
    
    for pais, count in paises:
        if pais:
            visitas_por_pais[pais] = count
    
    # Visitas por ciudad
    visitas_por_ciudad = {}
    ciudades = db.query(Visita.ciudad, func.count(Visita.id)).filter(
        Visita.ciudad.isnot(None)
    ).group_by(Visita.ciudad).all()
    
    for ciudad, count in ciudades:
        if ciudad:
            visitas_por_ciudad[ciudad] = count
    
    # Visitas recientes (últimas 10)
    visitas_recientes = db.query(Visita).order_by(
        Visita.fecha.desc()
    ).limit(10).all()
    
    visitas_recientes_list = []
    for v in visitas_recientes:
        visitas_recientes_list.append({
            "id": v.id,
            "pagina": v.pagina,
            "pais": v.pais,
            "ciudad": v.ciudad,
            "fecha": v.fecha.isoformat() if v.fecha else None
        })
    
    return EstadisticasVisitas(
        total_visitas=total_visitas,
        visitas_por_mes=visitas_por_mes,
        visitas_por_pais=visitas_por_pais,
        visitas_por_ciudad=visitas_por_ciudad,
        visitas_recientes=visitas_recientes_list
    )

@router.get("/", response_model=List[VisitaResponse])
def listar_visitas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Listar todas las visitas"""
    visitas = db.query(Visita).order_by(Visita.fecha.desc()).offset(skip).limit(limit).all()
    return visitas
