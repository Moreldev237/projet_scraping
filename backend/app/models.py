from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum, Float, JSON
from sqlalchemy.sql import func
from .database import Base
import enum

class TypeOpportunite(str, enum.Enum):
    EMPLOI = "emploi"
    BOURSE_SCOLAIRE = "bourse_scolaire"
    BOURSE_UNIVERSITAIRE = "bourse_universitaire"
    STAGE = "stage"
    CONCOURS = "concours"

class StatutOpportunite(str, enum.Enum):
    ACTIF = "actif"
    EXPIRE = "expire"
    EN_ATTENTE = "en_attente"
    INVALIDE = "invalide"

class Opportunite(Base):
    __tablename__ = "opportunites"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(500), nullable=False)
    description = Column(Text)
    type = Column(Enum(TypeOpportunite), nullable=False)
    source = Column(String(200), nullable=False)  # URL ou nom de la source
    source_url = Column(String(500))
    date_publication = Column(DateTime, server_default=func.now())
    date_limite = Column(DateTime, nullable=True)
    lieu = Column(String(200))
    pays = Column(String(100), default="Cameroun")
    organisation = Column(String(200))
    email_contact = Column(String(200))
    site_web = Column(String(500))
    statut = Column(Enum(StatutOpportunite), default=StatutOpportunite.EN_ATTENTE)
    tags = Column(JSON, default=list)  # Mots-clés pour la recherche
    hash_unique = Column(String(64), unique=True, index=True)  # Pour éviter les doublons
    date_scraping = Column(DateTime, server_default=func.now())
    est_active = Column(Boolean, default=True)
    niveau_etude = Column(String(100))  # Pour les bourses
    montant = Column(String(100))  # Montant de la bourse ou salaire

    def __repr__(self):
        return f"<Opportunite {self.titre}>"