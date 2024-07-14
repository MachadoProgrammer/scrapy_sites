# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join

def remove_quotes(text):
    return text.replace(u"\u201c", '').replace(u"\u201d", '')

def remove_whiteSpace(text):
    return text.strip()

def upperName(text):
    return text.upper()

def replace_comma(text):
    return text.replace(',', ';')



class CitacaoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    frase = scrapy.Field(
        input_processor=MapCompose(remove_whiteSpace, remove_quotes),
        output_processor=TakeFirst()
    )
    autor = scrapy.Field(
        output_processor=TakeFirst()
    )
    tags = scrapy.Field(
        output_processor=Join(',')
    )
    

class QuotacaoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    quote = scrapy.Field(
        input_processor=MapCompose(remove_quotes, remove_whiteSpace),
        output_processor=TakeFirst()
    )
    author = scrapy.Field(
        input_processor=MapCompose(upperName, remove_whiteSpace),
        output_processor=TakeFirst() # Mesma que o get() do xpath
    )
    tags = scrapy.Field(
        output_processor=Join(';')
    )