from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from .models import TypeOpportunite, StatutOpportunite

class OpportuniteBase(BaseModel):
    titre: str
    description: Optional[str] = None
    type: TypeOpportunite
    source: str
    source_url: Optional[str] = None
    date_limite: Optional[datetime] = None
    lieu: Optional[str] = None
    pays: Optional[str] = "Cameroun"
    organisation: Optional[str] = None
    email_contact: Optional[EmailStr] = None
    site_web: Optional[str] = None
    tags: Optional[List[str]] = []
    niveau_etude: Optional[str] = None
    montant: Optional[str] = None

class OpportuniteCreate(OpportuniteBase):
    hash_unique: str

class OpportuniteUpdate(BaseModel):
    statut: Optional[StatutOpportunite] = None
    est_active: Optional[bool] = None

class OpportuniteResponse(OpportuniteBase):
    id: int
    statut: StatutOpportunite
    date_publication: datetime
    date_scraping: datetime
    est_active: bool

    class Config:
        from_attributes = True

class OpportuniteSearch(BaseModel):
    query: Optional[str] = None
    type: Optional[TypeOpportunite] = None
    statut: Optional[StatutOpportunite] = None
    pays: Optional[str] = None
    organisation: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    tags: Optional[List[str]] = []