# -*- coding: utf-8 -*-

import sys
import scrapy
from scrapy.loader import ItemLoader
from crawlbot.items import CrawlbotItem, ProductItem, CombinationItem, init_file
from crawlbot.settings import CRAWLING_SITES
from crawlbot import settings
import hashlib


class YodySpider(scrapy.Spider):

    start_urls = ['https://canifa.com/']
    name = "test"

    def parse(self, response):

        for url in response.css('ul.ms-topmenu li'):
            a_element_url= url.css('a::attr(href)').extract_first()
            name= url.css('a::text').extract_first().strip()
            a_element_url= response.urljoin(a_element_url)
            # yield {
            #     "a_element": a_element_url,
            #     "name": name
            # }
            request= scrapy.Request(a_element_url, callback= self.parse_first_level, meta= {'root_url': a_element_url, 'root_name': name})
            yield request
    
    def parse_first_level(self, response):

        for a_element in response.css('ul.submenu li'):
            url= a_element.css('a::attr(href)')[0].extract()
            name= a_element.css('a span::text').extract()
            if name is None:
                name= name2
            if name is not None and len(name)> 0:
                name= name[0]
            # url= response.urljoin(url)
            # request
            # yield {
            #     "a_element_url": url,
            #     "name": name,
            # }
            request= scrapy.Request(url, callback= self.parse_second_level, meta= {'root_url': url, 'root_name': name})
            yield request

        # for elements in response.css('ul.main_item_left'):
        #     url =elements.css('a::attr(href)').extract()
        #     names = elements.css('a::text').extract()
        #     for uri in url:
        #         name = names[url.index(uri)]
        #         uri = response.urljoin(uri)
        #         request = scrapy.Request(uri, callback=self.parse_second_level,
        #         meta={"root_url": [response.meta['root_url'], uri], 'root_name': [response.meta['root_name'],name] })
        #         yield request
    
    def parse_second_level(self, response):
        product_urls= response.css('div.category-products ul li div.product-info div.category-product-list-item-description')
        for product_url in product_urls:
            url= product_url.css('a::attr(href)')[0].extract()
            name= product_url.css('a::text').extract()
            if name is None:
                name= name2
            if name is not None and len(name)>0:
                name= name[0]
            request= scrapy.Request(url, callback= self.parse_detail2, meta= {'root_url': url, 'root_name': name})
            yield request

    def parse_detail2(self, response):
        #get set of image url
        image_urls= response.css('#product_addtocart_form > div.product-img-box > div.more-views > ul li a img::attr(src)').extract()
        name= response.css('#product_addtocart_form > div.product-info-right > div.product-shop > div.product-name > span::text').extract_first()

        loader= ItemLoader(CrawlbotItem(), image_urls)
        image_urls = ['https:' + i for i in image_urls]

        loader.add_value('image_urls', image_urls)
        
        #get detail
        sizes= response.css('div.input-box ul li a::attr(title)').extract()
        yield{
            'size': sizes,
        }
        
        oldPrice = response.css('div.price-info div.price-box span.regular-price span.price::text')[0].extract()
        newPrice = []
        if oldPrice is None:
            oldPrice= response.css('#product_addtocart_form > div.product-info-right > div.product-shop > div.price-info > div > p.old-price span.price::text')[0].extract_first()
            newPrice= response.css('#product_addtocart_form > div.product-info-right > div.product-shop > div.price-info > div > p.special-price span::text')[0].extract_first()
        yield{
            'old': oldPrice,
            'new': newPrice
        }

        productItem= ProductItem()
        productItem.product["name"]= name.replace(',','')
        productItem.product["price_tex"]= oldPrice.replace('đ', '').replace('.','')
        productItem.product['manufacturer']= CRAWLING_SITES[self.start_urls[0]]['brand']
        ima_url = loader._values['image_urls']
        ima_url = [ CRAWLING_SITES[self.start_urls[0]]['image_dir'] + 'full/' + hashlib.sha1(i.encode('utf-8')).hexdigest() + '.jpg' for i in ima_url]
        productItem.product['image'] = ','.join(i for i in ima_url)
        productItem.set_alt_image()
        productItem.product['product_url'] = ''.join(i for i in response.meta['root_url']) 
        productItem.product['categories_url'] = response.request.url
        productItem.product['category'] = ''.join(i for i in response.meta['root_name'])

        # if newPrice is not None:
        #     productItem.product['reduction_from'] = newPrice.replace('đ','').replace('.','')
        #     productItem.set_reduction_price()

        if productItem.product['image'].find('images') == 0:
            
            productItem.write_to_csv(CRAWLING_SITES[self.start_urls[0]]['data_file'])


        
        if sizes is not None and len(sizes) > 0:
            combination_item = CombinationItem()

            for size in sizes:
                combination_item.set_attribute(size)
                combination_item.set_wholesale_price(oldPrice.replace(',', ''))
                combination_item.set_product_reference()
                combination_item.combination['group'] = 'Size:12'

                #write combination to csv file
                if size is not None:
                    combination_item.write_to_csv(CRAWLING_SITES[self.start_urls[0]]['data_file'])
        
        # # save images 
        yield loader.load_item()


        
