# Web Scraping de Livros

## Sobre o Projeto

Este é um script em Python que realiza web scraping no site [Books to Scrape](http://books.toscrape.com). Ele foi desenvolvido para extrair informações de todos os livros listados no catálogo, como **nome, preço e URL**, e salvar os dados de forma organizada em um arquivo Excel (`Itens.xlsx`).

O projeto demonstra habilidades em automação, manipulação de dados e boas práticas de desenvolvimento, como processamento paralelo e logging.

Repositório no GitHub: [MateusFerreiraM/Web-Scraping](https://github.com/MateusFerreiraM/Web-Scraping.git)

## Funcionalidades

- **Descoberta Automática de Páginas:** Identifica automaticamente o número total de páginas do catálogo, tornando o scraper adaptável a mudanças no site.
- **Extração de Dados em Paralelo:** Utiliza `ThreadPoolExecutor` para fazer requisições concorrentes, acelerando significativamente o processo de coleta de dados.
- **Tratamento de Erros:** O script lida com possíveis falhas de conexão ou extração de dados, garantindo que o programa não pare inesperadamente.
- **Logging Profissional:** Todas as atividades e erros são registrados em um arquivo de log (`relatorio_scraping.log`) para facilitar depuração e monitoramento.
- **Relatório Formatado:** Gera um arquivo Excel (`Itens.xlsx`) com a coluna de preços já formatada como moeda (£), entregando um resultado final limpo e profissional.

## Como Executar

### Pré-requisitos

- Python 3 instalado
- As bibliotecas listadas em `requirements.txt`

### Instalação

1. Clone o repositório para sua máquina:
    ```bash
    git clone https://github.com/MateusFerreiraM/Web-Scraping.git
    ```

2. Acesse a pasta do projeto:
    ```bash
    cd Web_Scraping
    ```

3. Instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```

### Execução

Para iniciar o scraping, execute o script principal:

```bash
python Scrape.py
```

### Saídas

Ao final da execução, dois arquivos serão gerados na pasta do projeto:

- **Itens.xlsx** → planilha com os dados dos livros (Nome, Preço, URL).
- **relatorio_scraping.log** → log detalhado da execução.

## Tecnologias Utilizadas

- **Python 3**
- **Bibliotecas:**
  - `requests`: para realizar as requisições HTTP.
  - `beautifulsoup4`: para fazer o parsing do HTML.
  - `pandas`: para manipulação dos dados e criação do arquivo Excel.
  - `openpyxl`: como motor para a escrita do arquivo `.xlsx`.