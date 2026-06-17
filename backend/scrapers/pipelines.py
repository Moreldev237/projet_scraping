from app.database import SessionLocal
from app import crud, schemas, models
from sqlalchemy.exc import IntegrityError
import re
from datetime import datetime

class OpportunitePipeline:
    def __init__(self):
        self.db = SessionLocal()
        
    def close_spider(self, spider):
        self.db.close()

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
        if not date_str:
            return None

        date_str = date_str.lower().strip()
        
        # Conversion des mois en français vers numérique
        mois = {
            'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
            'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
            'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
        }
        
        for nom, num in mois.items():
            date_str = date_str.replace(nom, num)

        # Nettoyage des caractères non numériques restant pour les formats standards
        for fmt in ("%d %m %Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None