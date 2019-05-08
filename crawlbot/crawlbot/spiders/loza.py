import scrapy
# -*- coding: utf-8 -*-
from scrapy.loader import ItemLoader
from crawlbot.items import CrawlbotItem, ProductItem, CombinationItem, init_file
from crawlbot.settings import CRAWLING_SITES
from crawlbot import settings
import hashlib


class KbFashionSpider(scrapy.Spider):

    start_urls = ['https://loza.vn/']
    name = CRAWLING_SITES[start_urls[0]]['spider_name']
    init_file(CRAWLING_SITES[start_urls[0]]['data_file'])
    custom_settings = {"IMAGES_STORE": CRAWLING_SITES[start_urls[0]]['image_dir']} 

    def parse(self, response):
        for elements in response.css('div.skip-content nav ol li'):
            url = elements.css('a::attr(href)').extract_first()
            name = elements.css('a::text').extract()[1].strip()
            url = response.urljoin(url)
            
            request = scrapy.Request(url, callback=self.parse_first_level,
            meta={'root_url': url, 'root_name': name })

            yield request
    
    def parse_first_level(self, response):
        product_urls = response.css('div.category-products ul li a::attr(href)').extract()
        for product_url in product_urls:
            product_url = response.urljoin(product_url)
            root_url = response.request.url
            name = response.meta['root_name']
            request = scrapy.Request(product_url, callback=self.parse_detail,
            meta={"root_url": root_url, "root_name": name})
            yield request

        next_page = response.css('div.toolbar-bottom div div a.next.i-next::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_first_level,meta={"root_name": response.meta['root_name']})

        
    
    def parse_detail(self, response):
        #set image_url and call pipeline
        image = response.css('div.more-views div.product-image-thumbs div a img::attr(src)').extract()
        loader = ItemLoader(item=CrawlbotItem(), selector=image)
        loader.add_value('image_urls', image)
        
        # get value for fields from web  
        name = response.css('div.product-shop div.product-name span::text').extract_first()

        description_p1 = response.css('div.tab-content div.std p::text').extract()
        description_p2 = response.css('div.tab-content div::text').extract()
        descriptions = description_p2[0:2] + description_p1
        description = ','.join(i.strip() for i in descriptions)

        price = response.css('div.price-info div span.price::text').extract()
        
        # set product
        product_item = ProductItem()
        product_item.product["name"] = name
        product_item.product["description"] = description.replace(',','').replace('\t','').replace('\r','')
        
        if price_tex is not None and len(price_tex) >3:
            price_tex = price[-1].strip()[0:-2].replace('.','')
            product_item.product["price_tex"] = price
            product_item.product['reduction_from'] = price[0].strip()[0:-2].replace('.','')
            product_item.set_reduction_price()

        product_item.product['manufacturer'] = CRAWLING_SITES[self.start_urls[0]]['brand']
        ima_url = loader._values['image_urls']
        ima_url = [ CRAWLING_SITES[self.start_urls[0]]['image_dir'] +'full/'+ hashlib.sha1(i.encode('utf-8')).hexdigest() + '.jpg' for i in ima_url]
        product_item.product['image'] = ','.join(i for i in ima_url)
        product_item.set_alt_image()
        product_item.product['product_url'] = response.request.url
        product_item.product['categories_url'] = response.meta['root_url']
        product_item.product['category'] = response.meta['root_name']
        sizes = response.css('dd.clearfix.swatch-attr.last ul.configurable-swatch-list.clearfix li a::attr(title)').extract()
        
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




        
