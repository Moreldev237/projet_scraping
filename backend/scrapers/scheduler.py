import schedule
import time
import os
import sys
from scrapers.spiders.emploi_spider import run_emploi_spider
from scrapers.spiders.bourses_spider import run_bourses_spider

def job_scrape_all():
    print(f"🔄 [{time.strftime('%Y-%m-%d %H:%M:%S')}] Début du scraping automatique...")
    try:
        # On s'assure que les spiders sont lancés
        run_emploi_spider()
        time.sleep(5) # Petit délai pour ne pas saturer le processeur
        run_bourses_spider()
        print("✅ Commandes de scraping envoyées avec succès")
    except Exception as e:
        print(f"❌ Erreur lors du scraping: {e}")

# Planifier le scraping
schedule.every().day.at("02:00").do(job_scrape_all)  # Tous les jours à 2h
schedule.every(6).hours.do(job_scrape_all)  # Toutes les 6 heures

if __name__ == "__main__":
    print("🚀 Scheduler démarré...")
    while True:
        schedule.run_pending()
        time.sleep(60)