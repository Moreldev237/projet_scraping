import schedule
import time
from app.database import SessionLocal
from scrapers.spiders.emploi_spider import run_emploi_spider
from scrapers.spiders.bourses_spider import run_bourses_spider

def job_scrape_all():
    print("🔄 Début du scraping automatique...")
    db = SessionLocal()
    try:
        run_emploi_spider(db)
        run_bourses_spider(db)
        print("✅ Scraping automatique terminé")
    except Exception as e:
        print(f"❌ Erreur lors du scraping: {e}")
    finally:
        db.close()

# Planifier le scraping
schedule.every().day.at("02:00").do(job_scrape_all)  # Tous les jours à 2h
schedule.every(6).hours.do(job_scrape_all)  # Toutes les 6 heures

if __name__ == "__main__":
    print("🚀 Scheduler démarré...")
    while True:
        schedule.run_pending()
        time.sleep(60)