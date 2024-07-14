import scrapy


class ProxyScraperSpider(scrapy.Spider):
  name = 'proxy_scraper'

  def start_requests(self):
    urls = [
      'https://www.sslproxies.org/',
    ]
    for url in urls:
      yield scrapy.Request(url=url, callback=self.parse)


  def parse(self, response):
    # Montar um xpath que retorna a linha
    for row in response.xpath('//table[@class="table table-striped table-bordered"]//tbody//tr'):
      yield {
        # Montar individualmente cada um que retorna o item daquela linha
        'ip': row.xpath('./td[1]/text()').get(),
        'port': row.xpath('./td[2]/text()').get(),
        'Code': row.xpath('./td[3]/text()').get(),
        'Country': row.xpath('./td[4]/text()').get(),
        'Anonymity': row.xpath('./td[5]/text()').get(),
        'Google': row.xpath('./td[6]/text()').get(),
        'Https': row.xpath('./td[7]/text()').get(),
        'Last Checked': row.xpath('./td[8]/text()').get(),
      }


      