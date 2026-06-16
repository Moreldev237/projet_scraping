import scrapy
from scrapy.crawler import CrawlerProcess
from scrapers.items import OpportuniteLoader
from app import crud
import re

class BoursesCamerounSpider(scrapy.Spider):
    name = "bourses_cameroun"
    
    # Sources de bourses pour le Cameroun
    start_urls = [
        'https://www.minesup.gov.cm/bourses/',
        'https://www.auf.org/offres/bourses/',
        'https://www.bourses-etudiants.com/cameroun/',
        'https://www.eunicas.fr/bourses/cameroun/',
        'https://www.unesco.org/fr/bourses',
        'https://www.bourses.gouv.cm/',
        'https://www.agenceuniversitaire.org/bourses/',
        'https://www.campusfrance.org/fr/bourses-d-etudes',
        # Bourses internationales
        'https://www.scholars4dev.com/country/cameroon/',
        'https://www.masterstudies.com/scholarships/cameroon/',
    ]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 3,
        'ROBOTSTXT_OBEY': True,
    }
    
    def parse(self, response):
        # Détection du type de bourse selon l'URL
        if 'bourses.gouv' in response.url:
            # Structure du site gouvernemental
            for bourse in response.css('div.bourse-item'):
                loader = OpportuniteLoader(selector=bourse)
                loader.add_css('titre', 'h2.title::text')
                loader.add_css('description', 'div.content::text')
                loader.add_css('organisation', 'div.organisme::text')
                loader.add_css('date_limite', 'div.deadline::text')
                loader.add_css('niveau_etude', 'div.niveau::text')
                loader.add_css('montant', 'div.montant::text')
                loader.add_value('type', 'bourse_universitaire')
                loader.add_value('source', response.url)
                loader.add_value('pays', 'Cameroun')
                
                titre = bourse.css('h2.title::text').get()
                if titre:
                    loader.add_value('hash_unique', crud.generate_hash(titre, response.url))
                
                yield loader.load_item()
        
        elif 'auf.org' in response.url:
            # Structure de l'AUF
            for offre in response.css('div.offre'):
                loader = OpportuniteLoader(selector=offre)
                loader.add_css('titre', 'h3 a::text')
                loader.add_css('description', 'div.description::text')
                loader.add_css('date_limite', 'div.date-limite::text')
                loader.add_css('organisation', 'div.organisation::text')
                loader.add_value('type', 'bourse_universitaire')
                loader.add_value('source', response.url)
                loader.add_value('pays', 'Cameroun')
                
                titre = offre.css('h3 a::text').get()
                if titre:
                    loader.add_value('hash_unique', crud.generate_hash(titre, response.url))
                
                yield loader.load_item()
        
        elif 'unesco' in response.url:
            # Bourses UNESCO
            for offre in response.css('div.unesco-item'):
                loader = OpportuniteLoader(selector=offre)
                loader.add_css('titre', 'h2::text')
                loader.add_css('description', 'p::text')
                loader.add_css('date_limite', 'span.date::text')
                loader.add_value('organisation', 'UNESCO')
                loader.add_value('source', response.url)
                loader.add_value('type', 'bourse_universitaire')
                
                titre = offre.css('h2::text').get()
                if titre:
                    loader.add_value('hash_unique', crud.generate_hash(titre, response.url))
                
                yield loader.load_item()
        
        # Pagination
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)

def run_bourses_spider(db_session):
    """Fonction pour exécuter le spider depuis l'API"""
    try:
        process = CrawlerProcess(get_project_settings())
        process.crawl(BoursesCamerounSpider)
        process.start()
    except Exception as e:
        print(f"Erreur lors du scraping: {e}")