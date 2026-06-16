from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from . import models, schemas
from datetime import datetime
import hashlib
import json

def create_opportunite(db: Session, opportunite: schemas.OpportuniteCreate):
    db_opportunite = models.Opportunite(**opportunite.model_dump())
    db.add(db_opportunite)
    db.commit()
    db.refresh(db_opportunite)
    return db_opportunite

def get_opportunite(db: Session, opportunite_id: int):
    return db.query(models.Opportunite).filter(models.Opportunite.id == opportunite_id).first()

def get_opportunites(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    search_params: schemas.OpportuniteSearch = None
):
    query = db.query(models.Opportunite).filter(models.Opportunite.est_active == True)
    
    if search_params:
        if search_params.query:
            query = query.filter(
                or_(
                    models.Opportunite.titre.ilike(f"%{search_params.query}%"),
                    models.Opportunite.description.ilike(f"%{search_params.query}%"),
                    models.Opportunite.organisation.ilike(f"%{search_params.query}%")
                )
            )
        if search_params.type:
            query = query.filter(models.Opportunite.type == search_params.type)
        if search_params.statut:
            query = query.filter(models.Opportunite.statut == search_params.statut)
        if search_params.pays:
            query = query.filter(models.Opportunite.pays == search_params.pays)
        if search_params.organisation:
            query = query.filter(models.Opportunite.organisation.ilike(f"%{search_params.organisation}%"))
        if search_params.tags:
            for tag in search_params.tags:
                query = query.filter(models.Opportunite.tags.contains([tag]))
        if search_params.date_debut:
            query = query.filter(models.Opportunite.date_publication >= search_params.date_debut)
        if search_params.date_fin:
            query = query.filter(models.Opportunite.date_publication <= search_params.date_fin)
    
    return query.order_by(models.Opportunite.date_publication.desc()).offset(skip).limit(limit).all()

def count_opportunites(db: Session, search_params: schemas.OpportuniteSearch = None):
    query = db.query(models.Opportunite).filter(models.Opportunite.est_active == True)
    if search_params and search_params.query:
        query = query.filter(
            or_(
                models.Opportunite.titre.ilike(f"%{search_params.query}%"),
                models.Opportunite.description.ilike(f"%{search_params.query}%")
            )
        )
    return query.count()

def update_opportunite_status(db: Session, opportunite_id: int, status: schemas.OpportuniteUpdate):
    db_opportunite = get_opportunite(db, opportunite_id)
    if db_opportunite:
        for key, value in status.model_dump(exclude_unset=True).items():
            setattr(db_opportunite, key, value)
        db.commit()
        db.refresh(db_opportunite)
    return db_opportunite

def generate_hash(titre: str, source: str, date_limite: str = ""):
    """Génère un hash unique pour éviter les doublons"""
    content = f"{titre.lower()}_{source.lower()}_{date_limite}"
    return hashlib.sha256(content.encode()).hexdigest()