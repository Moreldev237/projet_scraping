import os

BOT_NAME = 'scrapers'

SPIDER_MODULES = ['scrapers.spiders']
NEWSPIDER_MODULE = 'scrapers.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 2
COOKIES_ENABLED = False

# Configuration des pipelines
ITEM_PIPELINES = {
    'scrapers.pipelines.OpportunitePipeline': 300,
}

# Logging
LOG_LEVEL = 'INFO'