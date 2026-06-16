import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapers.items import OpportuniteLoader
from app import crud, models, schemas
from app.database import SessionLocal
from datetime import datetime
import re

class EmploiCamerounSpider(scrapy.Spider):
    name = "emploi_cameroun"
    
    # Sources d'emploi au Cameroun
    start_urls = [
        'https://www.emploi.cm/offres-emploi-cameroun',
        'https://www.camerounjobs.com/emploi/',
        'https://www.eco-mobilite.com/cameroun/offres-emploi/',
        'https://www.linkedin.com/jobs/search/?location=Cameroun',
        'https://www.lejobcameroun.com/emploi/',
        'https://www.francophonie.org/emplois',
        # Ajouter les sites gouvernementaux
        'https://www.minepat.gov.cm/emplois/',
        'https://www.onisep.fr/emploietg',
    ]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 3,
        'ROBOTSTXT_OBEY': True,
    }
    
    def parse(self, response):
        # Adapter selon la structure de chaque site
        # Exemple pour emploi.cm
        if 'emploi.cm' in response.url:
            for offre in response.css('div.job-item'):
                loader = OpportuniteLoader(selector=offre)
                loader.add_css('titre', 'h3.job-title a::text')
                loader.add_css('organisation', 'div.company-name::text')
                loader.add_css('lieu', 'div.location::text')
                loader.add_css('date_limite', 'div.date::text')
                loader.add_xpath('description', './/p[@class="description"]/text()')
                loader.add_value('type', 'emploi')
                loader.add_value('source', response.url)
                loader.add_value('source_url', response.url)
                loader.add_value('pays', 'Cameroun')
                
                # Générer un hash unique
                titre = offre.css('h3.job-title a::text').get()
                if titre:
                    loader.add_value('hash_unique', crud.generate_hash(titre, response.url))
                
                yield loader.load_item()
        
        # Gérer la pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)

def run_emploi_spider(db_session):
    """Fonction pour exécuter le spider depuis l'API"""
    try:
        process = CrawlerProcess(get_project_settings())
        process.crawl(EmploiCamerounSpider)
        process.start()
    except Exception as e:
        print(f"Erreur lors du scraping: {e}")