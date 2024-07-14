from cx_Freeze import setup, Executable

# Opções de build, incluindo pacotes adicionais necessários
build_exe_options = {
    "packages": ["os", "scrapy", "twisted", "lxml", "w3lib", "cssselect"],  # Adicione outros pacotes conforme necessário
    "excludes": ["tkinter"],  # Exclua pacotes não necessários
    "include_files": [("varredor_de_sites/items.py", "varredor_de_sites/pipelines.py")]  # Inclua arquivos adicionais necessários
}

# Configuração do executável
setup(
    name="Proxy Scraper and Checker",
    version="0.1",
    description="A simple proxy scraper and checker",
    options={"build_exe": build_exe_options},
    executables=[Executable("proxyscraper.py", base=None)]  # Caminho para o script principal
)