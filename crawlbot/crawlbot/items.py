# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from collections import OrderedDict
import csv


class CrawlbotItem(scrapy.Item):
    images = scrapy.Field()
    image_urls = scrapy.Field()


class ProductItem():

    def __init__(self):
        self.product = OrderedDict([
            ("type","PRODUCT"),
            ("id", ""),
            ("active", "1"),
            ("name", None),                  #name
            ("category", ""),              #category
            ("price_tex", ""),             #price
            ("id_tax_rules_group", "1"),
            ("wholesale_price", ""),
            ("on_sale", "0"),              #onsale 0/1
            ("reduction_price", ""),
            ("reduction_percent", ""),
            ("reduction_from", ""),
            ("reduction_to", ""),
            ("reference", ""),
            ("supplier_reference", ""),
            ("supplier", ""),
            ("manufacturer", ""),          #manufacturer (brand)
            ("ean13", ""),
            ("upc", ""),
            ("ecotax", ""),
            ("width", ""),
            ("height", ""),
            ("depth", ""),
            ("weight", ""),
            ("quantity", "100"),
            ("minimal_quantity", "1"),
            ("visibility", ""),
            ("additional_shipping_cost", ""),
            ("unity", ""),
            ("unit_price", ""),
            ("description_short", ""),
            ("description", ""),
            ("tags", ""),
            ("meta_title", ""),
            ("meta_keywords", ""),
            ("meta_description", ""),
            ("link_rewrite", ""),
            ("available_now", "In Stock"),
            ("available_later", ""),
            ("available_for_order", "1"),
            ("available_date", ""),
            ("date_add", ""),
            ("show_price", "1"),
            ("image", ""),                #image lists
            ("image_alt", ""),
            ("delete_existing_images", "0"),
            ("features", ""),
            ("online_only", "0"),
            ("condition", "new"),
            ("customizable", "0"),
            ("uploadable_files", "0"),
            ("text_fields", "0"),
            ("out_of_stock", "0"),
            ("is_virtual", "0"),
            ("file_url", "0"),
            ("nb_downloadable", "0"),
            ("date_expiration", "0"),
            ("product_url", ""),
            ("categories_url", "")
        ])

    def write_to_csv(self, file):

        with open(file, mode='a+') as file_csv:
            file_writer = csv.writer(file_csv, delimiter=';', quotechar='"',
            quoting=csv.QUOTE_MINIMAL)
            values = list(self.product.values())
            file_writer.writerow(values)

    def set_reduction_price(self):
        a = float(self.product['price_tex'])
        b = float(self.product['reduction_from'])

        if a is not None and b is not None:
            self.product['reduction_price'] = str(b-a)
            self.product['reduction_percent'] = str(int(round((b-a)/b, 2)*100))
    
    def set_alt_image(self):
        image_length = len(self.product['image'].split(','))
        name = self.product['name'].replace(',', ' ')
        self.product['image_alt'] = ','.join(i for i in [name]*image_length)


class CombinationItem():

    def __init__(self):
        self.combination = OrderedDict([
            ("import_type", 'COMBINATION'),
            ("id_product", ""),
            ("product_reference", ""),
            ("group", ""),
            ("attribute", ""),
            ("supplier_reference", ""),
            ("reference", ""),
            ("ean13", ""),
            ("upc", ""),
            ("wholesale_price", ""),
            ("price", ""),
            ("ecotax", ""),
            ("quantity", ""),
            ("minimal_quantity", ""),
            ("low_stock_threshold", ""),
            ("low_stock_alert", ""),
            ("weight", ""),
            ("default_on", ""),
            ("available_date", ""),
            ("image_position", ""),
            ("image_url", ""),
            ("image_alt", ""),
            ("shop", ""),
            ("advanced_stock_management", "")
        ])

    def write_to_csv(self, file):
        with open(file, mode='a+') as file_csv:
            file_writer = csv.writer(file_csv, delimiter=';', quotechar='"',
             quoting=csv.QUOTE_MINIMAL)
            values = list(self.combination.values())
            file_writer.writerow(values)

    def set_attribute(self, size):
        if size == 'S':
            self.combination['attribute']= '2/S'
            self.combination['supplier_reference'] = '2/S'
        elif size == 'M':
            self.combination['attribute'] = '4/M'
            self.combination['supplier_reference'] = '4/M'
        elif size == 'L':
            self.combination['attribute'] = '6/L'
            self.combination['supplier_reference'] = '6/L'
        elif size == 'XL':
            self.combination['attribute'] = '8/XL'
            self.combination['supplier_reference'] = '8/XL'
        elif size == 'XXL':
            self.combination['attribute'] = '10/XXL'
            self.combination['supplier_reference'] = '10/XXL'
        elif size == 'XXXL':
            self.combination['attribute'] = '12/XXXL'
            self.combination['supplier_reference'] = '12/XXXL'
        elif size == 'XXXXL':
            self.combination['attribute'] = '14/XXXXL'
            self.combination['supplier_reference'] = '14/XXXXL'
            
    
    def set_wholesale_price(self, price):
        self.combination['wholesale_price'] = price

    def set_product_reference(self):
        self.combination['product_reference'] = 'Size:select:1'


def init_file(file_name):
    with open(file_name, mode='a+') as file_csv:
        file_writer = csv.writer(file_csv, delimiter=';', quotechar='"',
            quoting=csv.QUOTE_MINIMAL)
        product_item = ProductItem()
        combination_item = CombinationItem()
        file_writer.writerow(list(product_item.product.keys()))
        file_writer.writerow(list(combination_item.combination.keys()))