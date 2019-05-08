import scrapy
# -*- coding: utf-8 -*-
from scrapy.loader import ItemLoader
from crawlbot.items import CrawlbotItem, ProductItem, CombinationItem, init_file
from crawlbot.settings import CRAWLING_SITES
from crawlbot import settings
import hashlib


class LozaSpider(scrapy.Spider):

    start_urls = ['http://kbfashion.vn/san-pham-p1.html']
    name = CRAWLING_SITES[start_urls[0]]['spider_name']
    init_file(CRAWLING_SITES[start_urls[0]]['data_file'])
    custom_settings = {"IMAGES_STORE": CRAWLING_SITES[start_urls[0]]['image_dir']} 

    def parse(self, response):
        elements = response.css('div.col-md-2.hidden-xs.hidden-sm ul')[0:1]
        for a_element in elements[0].css('li')[2:]:
            url = a_element.css('a::attr(href)').extract_first()
            url = response.urljoin(url)
            name = a_element.css('a::attr(title)').extract_first()

            request = scrapy.Request(url,callback=self.parse_first_level,meta={"root_name": name})
            yield request
    
    def parse_first_level(self, response):
        product_urls = response.css("div.col-md-3.col-xs-6 div div.col-md-12 a::attr(href)").extract()
        for product_url in product_urls:
            product_url = response.urljoin(product_url)
            name = response.meta['root_name']
            request = scrapy.Request(product_url,callback=self.parse_detail,meta={"root_url": response.request.url,"root_name":name})
            
            yield request
        
    
    def parse_detail(self, response):
        #set image_url and call pipeline
        image = response.css('div.swiper-wrapper')[1].css('a::attr(href)').extract()
        image = [response.urljoin(url) for url in image]
        loader = ItemLoader(item=CrawlbotItem(), selector=image)
        loader.add_value('image_urls', image)
        
        # get value for fields from web  
        name_p1 = response.css('div.col-sm-12 h3::text').extract_first()
        name_p2 = response.css('div.row div.col-sm-12::text').extract()[2].strip()
        name = name_p1 + name_p2

        price_tex = response.css('div.col-sm-12.price::text').extract_first()
        reduction_from = response.css('div.col-sm-12.price-line-through::text').extract_first()
        description = response.css('#content-wrapper > section > div:nth-child(3) > div > div.col-sm-7 > div:nth-child(4) > div p::text').extract_first()
        
        # set product
        product_item = ProductItem()
        product_item.product["name"] = name
        if description is not None:
            product_item.product["description"] = description
        
        if price_tex is not None and len(price_tex) >3:
            price_tex = price_tex.strip()[0:-1].replace('.','')
            product_item.product["price_tex"] = price_tex

        if reduction_from is not None:
            product_item.product['reduction_from'] = reduction_from.strip()[0:-1].replace('.','')
            product_item.set_reduction_price()

        product_item.product['manufacturer'] = CRAWLING_SITES[self.start_urls[0]]['brand']
        ima_url = loader._values['image_urls']
        ima_url = [ CRAWLING_SITES[self.start_urls[0]]['image_dir'] + 'full' + hashlib.sha1(i.encode('utf-8')).hexdigest() + '.jpg' for i in ima_url]
        product_item.product['image'] = ','.join(i for i in ima_url)
        product_item.set_alt_image()
        product_item.product['product_url'] = response.request.url
        product_item.product['categories_url'] = response.meta['root_url']
        product_item.product['category'] = response.meta['root_name']

        sizes = response.css('div.col-xs-10.attribut-wrapper')[0].css('label a::text').extract()
        
        # # write product to csv file
        if product_item.product['image'].find('images') == 0:
            product_item.write_to_csv(CRAWLING_SITES[self.start_urls[0]]['data_file'])

        # set a combination
        if sizes is not None and len(sizes) > 0:
            combination_item = CombinationItem()

            for size in sizes:
                combination_item.set_attribute(size)
                combination_item.set_wholesale_price(price_tex)
                combination_item.set_product_reference()
                combination_item.combination['group'] = 'Size:12'

                #write combination to csv file
                if size is not None:
                    combination_item.write_to_csv(CRAWLING_SITES[self.start_urls[0]]['data_file'])
        
        # # save images 
        yield loader.load_item()




        
