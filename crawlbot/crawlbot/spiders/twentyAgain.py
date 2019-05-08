# -*- coding: utf-8 -*-

import scrapy
from scrapy.loader import ItemLoader
from crawlbot.items import CrawlbotItem, ProductItem, CombinationItem, init_file
from crawlbot.settings import CRAWLING_SITES
from crawlbot import settings
import hashlib

class TwentyAgain(scrapy.Spider):
    start_urls= ["https://20again.vn/"]
    # name= CRAWLING_SITES[start_url[0]]['spider_name']
    # start_urls= ['https://20again.vn/phu-kien/quan-tat/quan-tat-b218n-paa003.html#92=261']
    name= "twentyAgain"
    init_file(CRAWLING_SITES[start_urls[0]]['data_file'])
    custum_setting= {"IMAGES_STORE": CRAWLING_SITES[start_urls[0]]['image_dir']}
    def parse(self, response):
        for item in response.css('ul.groupdrop-link li')[1:]:
            ele = item.css('a::attr(href)').extract_first()
            name= item.css('a::text').extract_first()
            # yield {
            #     "ele": ele,
            # }
            request= scrapy.Request(ele, self.parse_1st_level, meta= {'root_url': ele, 'root_name': name})
            yield request

        
    def parse_1st_level(self, response):
        items= response.css('div.cdz-product-top a::attr(href)').extract()
        # names= response.css('div.product-item-details')
        if items is not None and len(items)> 1:
            for item in items:
                # name= response.css('div.product-item-details a::text').extract()
                request= scrapy.Request(item, self.parse_detail, meta= {"root_url":response.meta["root_url"],"root_name": response.meta["root_name"]})
                # yield{
                #     'item': item,
                #     # 'name': name
                # }
                yield request


    def parse_detail(self, response):
        images= response.css('#amasty_gallery a::attr(href)').extract()
        if images is None or len(images)<1:
            images= response.css('div.product-image img::attr(data-zoom-image)').extract()
        name= response.css('div.product-name h1::text').extract()[0]
        loader= ItemLoader(item=CrawlbotItem(), selector= images)
        loader.add_value('image_urls', images)
        price_tex= response.css('div.price-box span span::text').extract_first()
        if price_tex is not None:
            price_tex= price_tex[:-2].replace('.','')
        sizes=[]
        for li_size in response.css('#configurable_swatch_size li'):
            sizes.append(li_size.css('a::attr(title)').extract()[0])
        
        product_item= ProductItem()
        product_item.product['name']= name
        product_item.product['price_tex']= price_tex

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
        if sizes is not None and len(sizes) > 0:
            combination_item = CombinationItem()

            for element in sizes:
                size = element.split('/')[0].strip()
                combination_item.set_attribute(size)
                # cost = element.split('-')[1][0:-1].replace(',', '.')
                combination_item.set_wholesale_price(price_tex)
                combination_item.set_wholesale_price(price_tex)
                combination_item.set_product_reference()
                combination_item.combination['group'] = 'Size:12'

                # write combination to csv file
                if size is not None:
                    combination_item.write_to_csv(CRAWLING_SITES[self.start_urls[0]]['data_file'])

        # save images 
        yield loader.load_item()

