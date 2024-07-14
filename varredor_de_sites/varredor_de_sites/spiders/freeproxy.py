import scrapy

class FreeProxyList(scrapy.Spider):
  name = 'freeproxy'

  def start_requests(self):
    urls = [
      'https://free-proxy-list.net/web-proxy.html',
    ]
    for url in urls:
      yield scrapy.Request(url=url, callback=self.parse)

  def parse(self, response):
    for element in response.xpath('//table[@class="table table-striped table-bordered"]//tbody/tr'):
      yield {
          'Proxy Name': element.xpath('./td[1]/a/text()').get(),
          'Domain': element.xpath('./td[2]/text()').get(),
          'Country': element.xpath('./td[3]/text()').get(),
          'Speed': element.xpath('./td[4]/text()').get(),
          'Popularity': element.xpath('./td[5]//div//div/text()').get(),
      }