# -*- coding: utf-8 -*-

# Scrapy settings for crawlbot project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'crawlbot'

SPIDER_MODULES = ['crawlbot.spiders']
NEWSPIDER_MODULE = 'crawlbot.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawlbot (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'crawlbot.middlewares.CrawlbotSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'crawlbot.middlewares.CrawlbotDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scrapy.pipelines.images.ImagesPipeline': 1,
}
# IMAGES_STORE = "images"

CRAWLING_SITES = {
    "https://elise.vn":{
        "brand":"Elise",
        "spider_name": "elise",
        "data_file":"elise_products.csv",
        "image_dir": "",
        "categories": {
        },
    },
    "https://canifa.com":{
        "brand":"Canifa",
        "spider_name": "canifa",
        "data_file":"canifa_products.csv",
        "image_dir": "",
        "categories": {
        },
    },
    "https://evy.com.vn":{
        "brand":"Evy",
        "spider_name": "evy",
        "data_file":"evy_products.csv",
        "image_dir": "",
        "categories": {
        },
    },
    "https://lamerfashion.com/":{
        "brand":"Lamer",
        "spider_name": "lamer",
        "data_file":"lamer.csv",
        "image_dir": "images/lamer",
        "categories": {
        },
    },
    "https://yody.vn/": {
        "brand": "Yody",
        "spider_name": "yody",
        "data_file": "yody.csv",
        "image_dir": "images/yody/",
        "categories": {

        }
    },
    "https://loza.vn/": {
        "brand": "Loza",
        "spider_name": "loza",
        "data_file": "loza.csv",
        "image_dir": "images/loza/",
        "categories": {

        },
    },
    "http://kbfashion.vn/san-pham-p1.html": {
        "brand": "KB Fashion ",
        "spider_name": "kb_fashion",
        "data_file": "kb_fashion.csv",
        "image_dir": "images/kb_fashion/",
        "categories": {

        },
    },
    "http://yoshino.com.vn/product-category/sp/": {
        "brand" : "Yoshino",
        "spider_name": "yoshino",
        "data_file": "yoshino.csv",
        "image_dir": "images/yoshino/",
        "categories": {

        },
    },
    "https://canifa.com/": {
        "brand": "Canifa",
        "spider_name": "canifa",
        "data_file": "canifa.csv",
        "image_dir": "images/canifa/",
        "categories": {

        },
    },
    "https://20again.vn/":{
        "brand": "20again",
        "spider_name": "twentyAgain",
        "data_file": "twentyAgain.csv",
        "image_dir": "images/twentyAgain/",
        "categories": {

        },
    }
    
    
}
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
