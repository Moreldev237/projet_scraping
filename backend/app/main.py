from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

from .database import engine, get_db
from . import models, schemas, crud
from scrapers.spiders.emploi_spider import run_emploi_spider
from scrapers.spiders.bourses_spider import run_bourses_spider

# Créer les tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Scraper Opportunités Cameroun", version="1.0.0")

# Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir les fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routes API
@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Scraper Opportunités Cameroun"}

@app.get("/api/opportunites", response_model=List[schemas.OpportuniteResponse])
async def get_opportunites(
    skip: int = 0,
    limit: int = 100,
    query: str = None,
    type: str = None,
    pays: str = None,
    organisation: str = None,
    db: Session = Depends(get_db)
):
    search_params = schemas.OpportuniteSearch(
        query=query,
        type=type,
        pays=pays,
        organisation=organisation
    )
    return crud.get_opportunites(db, skip=skip, limit=limit, search_params=search_params)

@app.get("/api/opportunites/{opportunite_id}", response_model=schemas.OpportuniteResponse)
async def get_opportunite(opportunite_id: int, db: Session = Depends(get_db)):
    opportunite = crud.get_opportunite(db, opportunite_id)
    if not opportunite:
        raise HTTPException(status_code=404, detail="Opportunité non trouvée")
    return opportunite

@app.post("/api/scrape/emploi")
async def scrape_emploi(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Déclenche le scraping des offres d'emploi"""
    background_tasks.add_task(run_emploi_spider, db)
    return {"message": "Scraping des offres d'emploi démarré en arrière-plan"}

@app.post("/api/scrape/bourses")
async def scrape_bourses(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Déclenche le scraping des bourses scolaires et universitaires"""
    background_tasks.add_task(run_bourses_spider, db)
    return {"message": "Scraping des bourses démarré en arrière-plan"}

@app.post("/api/scrape/all")
async def scrape_all(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Déclenche le scraping de toutes les sources"""
    background_tasks.add_task(run_emploi_spider, db)
    background_tasks.add_task(run_bourses_spider, db)
    return {"message": "Scraping de toutes les sources démarré en arrière-plan"}

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Retourne des statistiques sur les opportunités"""
    total_emploi = len(crud.get_opportunites(db, search_params=schemas.OpportuniteSearch(type="emploi")))
    total_bourses = len(crud.get_opportunites(db, search_params=schemas.OpportuniteSearch(type="bourse_universitaire")))
    total_bourses_scolaires = len(crud.get_opportunites(db, search_params=schemas.OpportuniteSearch(type="bourse_scolaire")))
    
    return {
        "total_opportunites": total_emploi + total_bourses + total_bourses_scolaires,
        "offres_emploi": total_emploi,
        "bourses_universitaires": total_bourses,
        "bourses_scolaires": total_bourses_scolaires,
        "dernier_scraping": "2026-06-16 10:00:00"  # À améliorer avec une table de logs
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)