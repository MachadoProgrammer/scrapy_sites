import scrapy
from scrapy.loader import ItemLoader
from varredor_de_sites.items import CitacaoItem

class QuotesToScrapeSpider(scrapy.Spider):
    # Identidade do spider
    name = 'frasebot'
    # request
    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    # response
    def parse(self, response):
        # aqui é onde voce deve processar o que é retornado da response
        # por exemplo, extrair informações da página
        for elemento in response.xpath('//div[@class="quote"]'):
            loader = ItemLoader(item=CitacaoItem(), selector=elemento, response=response)
            loader.add_xpath('frase', './/span[@class="text"]/text()')
            loader.add_xpath('autor', './/span/small[@class="author"]/text()')
            loader.add_xpath('tags', './/a[@class="tag"]/text()')
            yield loader.load_item()
            
        # Aqui é onde voce deve seguir para a próxima página
        # Tentar seguir para a próxima página, se existir varrer os dados
        try:
            next_page = response.xpath('//li[@class="next"]/a/@href').get()
            if next_page is not None:
                next_page_full = response.urljoin(next_page)
                yield scrapy.Request(url=next_page_full, callback=self.parse)
            # Se não existir, parar a execução
        except Exception as e:
            self.log('Não há mais páginas')

