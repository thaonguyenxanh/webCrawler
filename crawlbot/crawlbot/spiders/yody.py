# -*- coding: utf-8 -*-

import sys
import scrapy
from scrapy.loader import ItemLoader
from crawlbot.items import CrawlbotItem, ProductItem, CombinationItem, init_file
from crawlbot.settings import CRAWLING_SITES
from crawlbot import settings
import hashlib


class YodySpider(scrapy.Spider):

    start_urls = ['https://yody.vn/']
    name = CRAWLING_SITES[start_urls[0]]['spider_name']
    init_file(CRAWLING_SITES[start_urls[0]]['data_file'])
    custom_settings = {"IMAGES_STORE": CRAWLING_SITES[start_urls[0]]['image_dir']} 

    def parse(self, response):
        for elements in response.css('div.col-lg-10.col-md-10 li.menu-li.hasChild'):
            url = elements.css('a::attr(href)').extract_first()
            name = elements.css('a span.title-main-menu::text').extract_first()
            url = response.urljoin(url)

            request = scrapy.Request(url, callback=self.parse_first_level,
            meta={'root_url': url, 'root_name': name })
            yield request
    
    def parse_first_level(self, response):

        for elements in response.css('ul.main_item_left'):
            url =elements.css('a::attr(href)').extract()
            names = elements.css('a::text').extract()
            for uri in url:
                name = names[url.index(uri)]
                uri = response.urljoin(uri)
                request = scrapy.Request(uri, callback=self.parse_second_level,
                meta={"root_url": [response.meta['root_url'], uri], 'root_name': [response.meta['root_name'],name] })
                yield request
    
    def parse_second_level(self, response):
        product_urls = response.css('div.product-item.product-index div.product-information a::attr(href)').extract()
        for product_url in product_urls:
            product_url = response.urljoin(product_url)
            root_url = response.meta['root_url']
            root_name = response.meta['root_name']
            request = scrapy.Request(product_url, callback=self.parse_detail,
            meta={"root_url": root_url, "root_name": root_name})
            yield request

        next_page = response.css('div.links div.paginator a.paging-next.ico.fa.fa-caret-right::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_first_level)

        
    
    def parse_detail(self, response):
        #set image_url and call pipeline
        image = response.css('#img-child > div > img::attr(data-src)').extract()
        image = ['https:' + i for i in image]
        loader = ItemLoader(item=CrawlbotItem(), selector=image)
        loader.add_value('image_urls', image)
        
        # get value for fields from web  
        name = response.css('div.thongtingia h1::text').extract_first()
        description_p1 = response.css('div.tab-content div p span span span::text').extract()
        description_p2 = response.css('div.tab-content div p span span font::text').extract()[0:1]
        description = description_p1 + description_p2
        price_tex = response.css('div.thongtingia div.price label::text').extract_first()
        reduction_from = response.css('div.thongtingia div.price span del::text').extract_first()
        sizes_colors_cost = response.css('div.attr p a::text').extract()
        
        # set product
        product_item = ProductItem()
        product_item.product["name"] = name
        product_item.product["description"] = '\n'.join(i for i in description).strip()
        product_item.product["price_tex"] = price_tex.replace(',', '')
        
        if reduction_from is not None:
            product_item.product['reduction_from'] = reduction_from.replace(',', '')
            product_item.set_reduction_price()

        product_item.product['manufacturer'] = CRAWLING_SITES[self.start_urls[0]]['brand']
        ima_url = loader._values['image_urls']
        ima_url = [ CRAWLING_SITES[self.start_urls[0]]['image_dir'] + 'full/' + hashlib.sha1(i.encode('utf-8')).hexdigest() + '.jpg' for i in ima_url]
        product_item.product['image'] = ','.join(i for i in ima_url)
        product_item.set_alt_image()
        product_item.product['product_url'] = response.request.url
        product_item.product['categories_url'] = ','.join(i for i in response.meta['root_url'])
        product_item.product['category'] = ','.join(i for i in response.meta['root_name'])
        
        # # write product to csv file
        if product_item.product['image'].find('images') == 0:
            product_item.write_to_csv(CRAWLING_SITES[self.start_urls[0]]['data_file'])

        # set a combination
        if sizes_colors_cost is not None and len(sizes_colors_cost) > 0:
            combination_item = CombinationItem()

            for size in sizes_colors_cost:
                combination_item.set_attribute(size)
                combination_item.set_wholesale_price(price_tex.replace(',', ''))
                combination_item.set_product_reference()
                combination_item.combination['group'] = 'Size:12'

                #write combination to csv file
                if size is not None:
                    combination_item.write_to_csv(CRAWLING_SITES[self.start_urls[0]]['data_file'])
        
        # # save images 
        yield loader.load_item()




        
