import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Join, MapCompose
import re

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class OpportuniteItem(scrapy.Item):
    titre = scrapy.Field(output_processor=TakeFirst())
    description = scrapy.Field(output_processor=Join())
    type = scrapy.Field(output_processor=TakeFirst())
    source = scrapy.Field(output_processor=TakeFirst())
    source_url = scrapy.Field(output_processor=TakeFirst())
    date_limite = scrapy.Field(output_processor=TakeFirst())
    lieu = scrapy.Field(output_processor=TakeFirst())
    organisation = scrapy.Field(output_processor=TakeFirst())
    email_contact = scrapy.Field(output_processor=TakeFirst())
    site_web = scrapy.Field(output_processor=TakeFirst())
    tags = scrapy.Field()
    niveau_etude = scrapy.Field(output_processor=TakeFirst())
    montant = scrapy.Field(output_processor=TakeFirst())
    hash_unique = scrapy.Field(output_processor=TakeFirst())

class OpportuniteLoader(ItemLoader):
    default_item_class = OpportuniteItem
    default_input_processor = MapCompose(clean_text)
    default_output_processor = TakeFirst()