from app.database import SessionLocal
from app import crud, schemas, models
from sqlalchemy.exc import IntegrityError
import re
from datetime import datetime

class OpportunitePipeline:
    def __init__(self):
        self.db = SessionLocal()
        
    def process_item(self, item, spider):
        # Convertir l'item en dictionnaire
        item_dict = dict(item)
        
        # Nettoyer et préparer les données
        if 'date_limite' in item_dict and item_dict['date_limite']:
            try:
                # Tentative de parsing de la date
                item_dict['date_limite'] = self.parse_date(item_dict['date_limite'])
            except:
                item_dict['date_limite'] = None
        
        # Définir le statut par défaut
        if 'statut' not in item_dict:
            item_dict['statut'] = 'actif'
        
        # Ajouter le hash unique s'il manque
        if 'hash_unique' not in item_dict or not item_dict['hash_unique']:
            item_dict['hash_unique'] = crud.generate_hash(
                item_dict.get('titre', ''),
                item_dict.get('source', '')
            )
        
        try:
            # Créer l'opportunité dans la base de données
            opportunite_data = schemas.OpportuniteCreate(**item_dict)
            crud.create_opportunite(self.db, opportunite_data)
            print(f"✅ Ajouté: {item_dict.get('titre', 'Sans titre')}")
        except IntegrityError:
            self.db.rollback()
            print(f"⏩ Doublon ignoré: {item_dict.get('titre', 'Sans titre')}")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erreur: {e}")
        
        return item
    
    def parse_date(self, date_str):
        """Tente de parser différentes formats de date"""
        patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{1,2}) (\w+) (\d{4})',
            r'(\d{1,2}) (janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre) (\d{4})',
        ]
        # Implémentation simplifiée
        return None