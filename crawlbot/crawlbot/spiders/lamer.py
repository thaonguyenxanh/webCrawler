# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from crawlbot.items import CrawlbotItem, ProductItem, CombinationItem, init_file
from crawlbot.settings import CRAWLING_SITES
from crawlbot import settings
import hashlib


class LamerSpider(scrapy.Spider):

    start_urls = ["https://lamerfashion.com/"]
    name = CRAWLING_SITES[start_urls[0]]['spider_name']
    init_file(CRAWLING_SITES[start_urls[0]]['data_file'])
    custom_settings = {"IMAGES_STORE": CRAWLING_SITES[start_urls[0]]['image_dir']}  
    
    def parse(self, response):
        for li_element in response.css('#navbar > div > ul > li'):
            urls = li_element.css('ul a::attr(href)').extract()

            if urls is not None:
                for url in urls:

                    if url is not None and len(url) > 0 and url.find('coll') > 0:
                        url = response.urljoin(url)
                        request = scrapy.Request(url, callback=self.parse_first_level)
                        yield request

    def parse_first_level(self, response):
        for item in response.css('div.product-item'):
            product_url = item.css('div.item-content a::attr(href)').extract_first()
            if product_url is not None:
                product_url = response.urljoin(product_url)
                yield scrapy.Request(
                    product_url, callback=self.parse_detail,
                    meta={
                        'root_url': response.request.url,
                        'root_name': response.css('div.row h1::text')
                    .extract_first().strip()
                    })

        next_page = response.css('div.pagination-default.clearfix.clear-ajax a.next.fa.fa-angle-right::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_first_level)

    def parse_detail(self, response):
        #set image_url and call pipeline
        image = response.css('#surround > div a::attr(data-image)').extract()
        image = ['https:' + i for i in image]
        loader = ItemLoader(item=CrawlbotItem(), selector=image)
        loader.add_value('image_urls', image)
        
        # get value for fields from web  
        name = response.css('div.product-title h1::text').extract_first()
        description_p1 = response.css('#tab_one > div > p::text').extract()
        description_p2 = response.css('#tab_one > div::text').extract()
        description = description_p1 + description_p2
        price_tex = response.css('div.product-price span::text').extract_first()
        reduction_from = response.css('div.product-price del::text').extract_first()
        sizes_colors_cost = response.css('#product-select > option::text').extract()
        
        # set product
        product_item = ProductItem()
        product_item.product["name"] = name
        product_item.product["description"] = '\n'.join(i for i in description).strip()
        product_item.product["price_tex"] = price_tex[0:-1].replace(',', '')
        
        if reduction_from is not None:
            product_item.product['reduction_from'] = reduction_from[0:-1].replace(',', '')
            product_item.set_reduction_price()

        product_item.product['manufacturer'] = CRAWLING_SITES[self.start_urls[0]]['brand']
        ima_url = loader._values['image_urls']
        ima_url = [CRAWLING_SITES[self.start_urls[0]]['image_dir'] + 'full/' + hashlib.sha1(i.encode('utf-8')).hexdigest() + '.jpg' for i in ima_url]
        product_item.product['image'] = ','.join(i for i in ima_url)
        product_item.set_alt_image()
        product_item.product['product_url'] = response.request.url
        product_item.product['categories_url'] = response.meta['root_url']
        product_item.product['category'] = response.meta['root_name']
        
        # write product to csv file
        if product_item.product['image'].find('images') == 0:
            product_item.write_to_csv(CRAWLING_SITES[self.start_urls[0]]['data_file'])

        # set a combination
        if sizes_colors_cost is not None and len(sizes_colors_cost) > 0:
            combination_item = CombinationItem()

            for element in sizes_colors_cost:
                size = element.split('/')[0].strip()
                combination_item.set_attribute(size)
                cost = element.split('-')[1][0:-1].replace(',', '.')
                combination_item.set_wholesale_price(cost)
                combination_item.set_wholesale_price(price_tex[0:-1].replace(',', ''))
                combination_item.set_product_reference()
                combination_item.combination['group'] = 'Size:12'

                #write combination to csv file
                if size is not None:
                    combination_item.write_to_csv(CRAWLING_SITES[self.start_urls[0]]['data_file'])

        # save images 
        yield loader.load_item()