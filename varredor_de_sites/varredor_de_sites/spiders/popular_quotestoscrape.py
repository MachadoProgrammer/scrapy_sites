import scrapy
from scrapy.loader import ItemLoader
from varredor_de_sites.items import QuotacaoItem

class PopularQuotesSpider(scrapy.Spider):
    name = 'popular_quotes'
    
    def start_requests(self):
        urls = [
            'https://www.goodreads.com/quotes?page={1}'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        for element in response.xpath('//div[@class="quoteDetails"]'):
            loader = ItemLoader(item=QuotacaoItem(), selector=element, response=response)
            loader.add_xpath('quote', './/div[@class="quoteText"]/text()')
            loader.add_xpath('author', './/span[@class="authorOrTitle"]/text()')
            loader.add_xpath('tags', './/div[@class="greyText smallText left"]/a/text()')
            yield loader.load_item()
            # Aqui é onde voce deve seguir para a próxima página
            # Extrair todas as citações, autores e tags da página
            # Exportar os dados para um arquivo csv
            try:
                next_page = response.xpath("//div/a[@class='next_page']/@href").get().split('=')[1]
                print('#' * 20)
                print(next_page)
                print('#' * 20)
                if next_page is not None:
                    next_page_full = f'https://www.goodreads.com/quotes?page={next_page}'
                    yield scrapy.Request(url=next_page_full, callback=self.parse)

            except Exception as e:
                self.log('Não há mais páginas')

                # Vamos atualizar a spider do site GoodReads
                # 1 - Remover todos os caracteres especiais \u2019 das frases
                # 2 - Colocar o nome de todos os autores em MAIÚSCULO
                # 3 - Remover os espaços em branco dentro das frases e autures
                # 4 - Mudar o separador das tags de uma vírgula, para um ponto e vírgula(;)