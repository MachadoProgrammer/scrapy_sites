# Mundo dos crawlers

  - Varrer sites para obter dados e exportar para: csv, xml, json, BD.
  
  -> Porque o arquivo Robots.txt é super importante ?
    - User-agent: nome do bot
    - Disallow: Uma lista de quais páginas ele não quer que sejam varridas

## Importar scrapy


- Iniciar amb. virtual 
- scrapy startproject nomedapasta
- Dentro da spider: criar um arquivo.py
  - import scrapy
  - configurar classe ex:  QuotesToScrapeSpider(scrapy.Spider)
    - exemplo de config. 
      * Identidade do spider
      name = 'frasebot'
      * request -> requisição
      def start_requests(self):
          urls = [
              'http://quotes.toscrape.com'
          ]
          for url in urls:
              yield scrapy.Request(url=url, callback=self.parse) 
      * response
      def parse(self, response):
          * aqui é onde voce deve processar o que é retornado da response
          * por exemplo, extrair informações da página
          with open('quotes.html', 'wb') as f:
              f.write(response.body)

## testar meu XPATH em TEMPO REAL
  - scrapy shell nomesite
  - response.xpath()

## Extração de dados

  - Pegar a tag pai e fazer o yield nas tags filho, ex:
  - yield {
                'texto': elemento.xpath('.//span[@class="text"]/text()').get(),
                'autor': elemento.xpath('.//span/small[@class="author"]/text()').get()
            }
            - O "." para buscar relativo onde voce indicou, sem isso, buscara no site todo
            - scrapy crawl frasebot -O dados.csv 

## EXTRAÇÃO de MÚLTIPLAS páginas


  --  Aqui é onde voce deve seguir para a próxima página
        - Montar uma url
          1. Pegar a url existente e juntar com o da proxima pagina(urljoin)
          2. Ou mudar apenas a numeração da página(caso de)
            - https://www.goodreads.com/quotes?page={1}, colocar na urls
            - e pegar o numero da proxima pagina
            - next_page_full = f'https://www.goodreads.com/quotes?page=     {next_page}'
                    yield scrapy.Request(url=next_page_full, callback=self.parse)

## Como EXPORTAR resultados para JSON, CSV ou XML

  - O para sobreescrever arquivos existentes
  - o para acrescentar dados ao arquivo existente(Não funciona com json)

  - scrapy crawl nomebot -O dados.json
  - scrapy crawl nomebot -O dados.xml
  - scrapy crawl nomebot -O dados.csv

## Como LIMPAR-PROCESSAR dados antes de salvar

  - Deixar no fromato que precisa e não no formato padrão
  -> items.py, onde vai estar processando os dados que estão sendo varridos
  
  -> Imports: from scrapy.loader.processors import MapCompose, TakeFirst, Join

  def remove_quotes(text):
    return text.replace(u"\u201c", '').replace(u"\u201d", '')

  def remove_whiteSpace(text):
    return text.strip()


  -> input_processor=MapCompose(remove_whiteSpace, remove_quotes) -> como os serao tratados
  -> output_processor=TakeFirst(',') -> como os dados irão sair

  - No seu arquivo principal from scrapy.loader import ItemLoader
  - from varredor_de_sites.items import CitacaoItem
  - loader = ItemLoader(item=CitacaoItem(), selector=elemento, response=response)
  - loader.add_xpath('frase', './/span[@class="text"]/text()')
            loader.add_xpath('autor', './/span/small[@class="author"]/text()')
            loader.add_xpath('tags', './/a[@class="tag"]/text()')
            yield loader.load_item()
            
  * MapCompose: Utilizado para aplicar uma sequência de funções a cada valor de entrada de um campo. 
  * É útil para processamento ou limpeza de dados. Por exemplo, se você precisa limpar espaços em branco 
  * e converter strings para números, você pode usar MapCompose para aplicar essas duas funções sequencialmente.

  * TakeFirst: Este processador pega o primeiro elemento não nulo de uma lista de valores. 
  * É útil quando você está interessado apenas no primeiro valor extraído, descartando o restante.

  * Join: Usado para juntar os elementos de uma lista em uma única string, utilizando um delimitador especificado. 
  * É útil quando você tem vários valores que precisam ser combinados em um único campo de texto.


## Como varrer tabelas

## Evitar bloqueios: User Agent / Proxy(Apenas Pago)
  - Delay 3s
  - Robot = False
  - User agent de forma aleatoria pip install scrapy-fake-useragent
  - add ao settings 
      -> DOWNLOADER_MIDDLEWARES = {
      'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
      'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
      'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
      'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
  }

  ## settings.py

  FAKEUSERAGENT_PROVIDERS = [
      'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # This is the first provider we'll try
      'scrapy_fake_useragent.providers.FakerProvider',  # If FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
      'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # Fall back to USER_AGENT value
  ]

  ## Set Fallback User-Agent
  USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203'

  ## Config de Proxy

  SCRAPEOPS_API_KEY = 'SUA_CHAVE_API'
  SCRAPEOPS_PROXY_ENABLED = True

  DOWNLOADER_MIDDLEWARES = {
      'scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk': 725,
  }



  ## Salvar numa planilha 
  from itemadapter import ItemAdapter
  import openpyxl
  from settings import XLSX_PATH

  *No settings: na ultima linha,  criar uma constante XLSX_PATH = 'nome.xlsx' e importar na pipeline
  *Descomentar ITEM_PIPELINES no settings
  varredor_de_sites.pipelines.XLSXPipeline

  CAMPOS = [] -> Nome das colunas

  class XLSXPipeline(object): -> nome da classe tem que ser o mesmo nome no ITEM_PIPELINE
      planikha = None
      sheet = None
      
      def open_spider(self, spider): -> criação do workbook
          self.planikha = openpyxl.Workbook()
          self.sheet = self.planikha.active
          self.sheet.append(CAMPOS)

      def process_item(self, item, spider): -> Processa os items
          adapter = ItemAdapter(item)
          self.sheet.append([adapter.get('Proxy Name'), adapter.get('Domain'), adapter.get('Country'), adapter.get('Speed'), adapter.get('Popularity')])
          return item
      
      def close_spider(self, spider):
          self.planikha.save(XLSX_PATH) -> passar a constante aqui importada
          self.planikha.close()


    scrapy crawl freeproxy  rodar o bot
        
    

## Salvar num banco de dados -> Pasta(Scraper_BancoDeDados)
    -  fazer as config na pipeline
        - abrir a conexao, fechar a conexao e processar os items
    - No settings, ITEM_PIPELINES -> colocar o nome da classe la: varredor_de_sites.pipelines.SQLitePipeline

## Como usar SELENIUM + SCRAPY p páginas com Javascript
    ex: import scrapy
        import logging
        from selenium.webdriver.remote.remote_connection import LOGGER
        from selenium.common.exceptions import *
        from selenium.webdriver.support import expected_conditions as CondicaoExperada
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from scrapy.selector import Selector
        from time import sleep
        
        
        def iniciar_driver():
            chrome_options = Options()
            LOGGER.setLevel(logging.WARNING)
            arguments = ['--lang=pt-BR', '--window-size=1920,1080', '--headless']
            for argument in arguments:
                chrome_options.add_argument(argument)
        
            chrome_options.add_experimental_option('prefs', {
                'download.prompt_for_download': False,
                'profile.default_content_setting_values.notifications': 2,
                'profile.default_content_setting_values.automatic_downloads': 1,
        
            })
            driver = webdriver.Chrome(service=ChromeService(
                ChromeDriverManager().install()), options=chrome_options)
        
            wait = WebDriverWait(
                driver,
                10,
                poll_frequency=1,
                ignored_exceptions=[
                    NoSuchElementException,
                    ElementNotVisibleException,
                    ElementNotSelectableException,
                ]
            )
            return driver, wait
        
        
        class F1RacesSpider(scrapy.Spider):
            # identidade
            name = 'f1racebot'
        
            # Request
            def start_requests(self):
                urls = ['https://f1races.netlify.app/']
        
                for url in urls:
                    yield scrapy.Request(url=url, callback=self.parse,meta={'next_url':url})
        
            # Response
            def parse(self, response):
                driver, wait = iniciar_driver()
                driver.get(response.meta["next_url"])
                sleep(10)
                response_webdriver = Selector(text=driver.page_source)
               
        
                for quote in response_webdriver.xpath("//div[@class='sc-bZQynM llbHfj']"):
                    yield {
                        'Grand Prix': quote.xpath("./div[1]/text()").get(),
                        'Local': quote.xpath("./div[2]/text()").get(),
                        'Piloto': quote.xpath(".//a/text()").get(),
                        'Tempo': quote.xpath("./div[4]/text()").get(),
                    }
                driver.close()

## Como ligar Scrapy a outros Programas SEM usar terminal
    import scrapy
    from scrapy.crawler import CrawlerProcess
    
    
    class QuotesToScrapeSpider(scrapy.Spider):
        # Identidade
        name = 'quotebot'
        # Request
    
        def start_requests(self):
            # Definir url(s) a varrer
            urls = ['https://www.goodreads.com/quotes']
    
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)
        # Response
    
        def parse(self, response):
            # aqui é onde você deve processar o que é retornado da response
            for elemento in response.xpath("//div[@class='quote']"):
                yield {
                    'frase': elemento.xpath(".//div[@class='quoteText']/text()").get(),
                    'autor': elemento.xpath(".//span[@class='authorOrTitle']/text()").get(),
                    'tags': elemento.xpath(".//div[@class='greyText smallText left']/a/text()").getall()
                }
    
    bot = CrawlerProcess(
        settings={
            "FEEDS": {
                "itens.csv": {"format":"csv"}
            }
        }
    )
    
    adicioanar configs

    bot = CrawlerProcess(
    settings={
        "FEEDS": {
            "itens.csv": {"format":"csv"}
        },
        "ROBOTSTXT_OBEY": True,  
        "USER_AGENT": 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        "ITEM_PIPELINES": {'myproject.pipelines.MyPipeline': 300},
    }
    )
    
    bot.crawl(QuotesToScrapeSpider)
    bot.start()

    No novo arquivo 
    from app import QuotesToScrapeSpider, CrawlerProcess

    resposta = input('Devo iniciar a automação? (s/n)')
    
    if resposta == 's':
        bot = CrawlerProcess(
        settings={
            "FEEDS": {
                "livros.json": {"format":"csv"}
            }
        }
        )
    
        bot.crawl(QuotesToScrapeSpider)
        bot.start()
    else:
        print('Não será iniciado a automação')

## Transformar o scrapy em um executavel
    from cx_Freeze import setup, Executable
    
    # Dependências do projeto
    build_exe_options = {
        "packages": ["os", "scrapy", "twisted"],  # Adicione outros pacotes necessários
        "excludes": ["tkinter"],  # Exclua pacotes não necessários
        "include_files": []  # Inclua outros arquivos necessários como databases, etc.
    }
    
    # Configuração do executável
    setup(
        name="NomeDoSeuProjeto",
        version="0.1",
        description="Descrição do seu projeto Scrapy",
        options={"build_exe": build_exe_options},
        executables=[Executable("caminho/do/seu/script.py", base=None)]  # caminho para o script que inicia o seu scrapy
    )

    from cx_Freeze import setup, Executable

    # Opções de build, incluindo pacotes adicionais necessários
    build_exe_options = {
        "packages": ["os", "scrapy", "twisted", "lxml", "w3lib", "cssselect"],  # Adicione outros pacotes conforme necessário
        "excludes": ["tkinter"],  # Exclua pacotes não necessários
        "include_files": [("varredor_de_sites/items.py", "varredor_de_sites/items.py")]  # Inclua arquivos adicionais necessários
    }
    
    # Configuração do executável
    setup(
        name="GoodReadsSpider",
        version="0.1",
        description="Scrapy Spider for GoodReads Quotes",
        options={"build_exe": build_exe_options},
        executables=[Executable("goodreads.py", base=None)]  # Caminho para o script principal
    )

    toda a pasta em um executavel

    from cx_Freeze import setup, Executable
    import os
    import sys
    
    # Inclui as pastas e arquivos necessários
    PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
    os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
    os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')
    
    # Opções adicionais para incluir arquivos e módulos
    build_exe_options = {
        "packages": ["os", "scrapy", "twisted", "openpyxl", "itemadapter", "lxml", "w3lib", "cssselect"],  # Adicione todos os pacotes usados
        "include_files": [
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
            # Inclua outros arquivos necessários aqui
        ],
        "excludes": ["tkinter", "PyQt5"],
    }
    
    # Defina o ponto de entrada do seu projeto Scrapy
    base = None
    if sys.platform == "win32":
        base = "Win32GUI"
    
    setup(
        name="NomeDoSeuProjeto",
        version="0.1",
        description="Descrição do seu projeto Scrapy",
        options={"build_exe": build_exe_options},
        executables=[Executable("script_de_entrada.py", base=base)]  # Substitua script_de_entrada.py pelo script que inicia seu projeto
    )

    com interface grafica
    import PySimpleGUI as sg
    import subprocess
    
    # Layout da interface gráfica
    layout = [
        [sg.Text("Pressione o botão para iniciar o Scrapy")],
        [sg.Button("Iniciar Scrapy")],
        [sg.Output(size=(60, 20))]
    ]
    
    # Criar a janela
    window = sg.Window("Scrapy GUI", layout)
    
    # Loop de eventos
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == "Iniciar Scrapy":
            # Substitua 'seu_script_scrapy.py' pelo script principal do seu projeto Scrapy
            subprocess.run(["scrapy", "crawl", "nome_do_seu_spider"])
    
    window.close()
    from cx_Freeze import setup, Executable

    build_exe_options = {
        "packages": ["os", "scrapy", "twisted", "openpyxl", "itemadapter", "lxml", "w3lib", "cssselect", "PySimpleGUI"],
        "excludes": ["tkinter"],
        "include_files": ["pipelines.py", "varredor_de_sites/"]  # Inclua outros arquivos ou diretórios necessários
    }
    
    base = None
    
    setup(
        name="ScrapyGUI",
        version="0.1",
        description="Scrapy Project with GUI",
        options={"build_exe": build_exe_options},
        executables=[Executable("gui.py", base=base)]
    )# scrapy_sites
