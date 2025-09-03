import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configura o logging para registrar a atividade do script no arquivo 'relatorio_scraping.log'.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('relatorio_scraping.log', mode='w', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_total_pages(url):
    """
    Descobre o número total de páginas a serem processadas.
    Faz uma única requisição à página inicial para encontrar o indicador de paginação (ex: "Page 1 of 50") e extrai o número total de páginas.
    """
    logger.info("Iniciando a descoberta do número total de páginas...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Localiza o elemento que contém a informação "Page 1 of 50"
        page_indicator = soup.find('li', class_='current')
        if not page_indicator:
            logger.warning("Indicador de páginas não encontrado. Assumindo uma única página.")
            return 1
        
        # Extrai o texto e usa uma expressão regular para encontrar o último número
        text = page_indicator.get_text(strip=True)
        # re.findall(r'\d+', text) encontra todos os números no texto.
        # [-1] pega o último, que corresponde ao total de páginas.
        total_pages = int(re.findall(r'\d+', text)[-1])
        logger.info(f"{total_pages} páginas encontradas.")
        return total_pages

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão ao descobrir total de páginas: {e}. Assumindo uma única página.")
        return 1
    except (IndexError, ValueError):
        logger.error("Não foi possível extrair o número de páginas do texto. Assumindo uma única página.")
        return 1


def fetch_and_parse_page(url, page_number):
    """
    Extrai nome, preço e URL dos livros de uma única página.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        
        page_books_data = []
        base_url_catalogue = "http://books.toscrape.com/catalogue/"
        
        for book in books:
            nome = book.h3.a['title']
            url_completa = base_url_catalogue + book.h3.a['href']
            
            preco_texto = book.find('p', class_='price_color').text
            preco_string = preco_texto.replace('£', '')
            # Converte o preço para float para permitir formatação numérica no Excel
            preco = float(preco_string)
            
            page_books_data.append({
                'Nome': nome,
                'Preço': preco,
                'URL': url_completa
            })
            
        return page_number, page_books_data
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Falha ao extrair dados da URL {url}: {e}")
        return page_number, None

def scrape_all_books():
    """
    Todo o processo de scraping e geração Excel.
    Executa as fases de: (1)Descoberta do total de páginas, (2)Extração de Dados, (3)Organização e Geração do Relatório .xlsx.
    """
    start_url = "http://books.toscrape.com/catalogue/page-1.html"
    
    # FASE 1: Descoberta do total de páginas
    total_pages = get_total_pages(start_url)
    if not total_pages:
        logger.critical("Não foi possível determinar o número de páginas. Encerrando o script.")
        return
    
    # Gera a lista de todas as tarefas a serem executadas
    tasks_to_run = [(f"http://books.toscrape.com/catalogue/page-{i}.html", i) for i in range(1, total_pages + 1)]

    # FASE 2: Extração de dados
    unordered_results = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        logger.info(f"Iniciando coleta de dados em paralelo para {total_pages} páginas...")
        
        future_to_task = {executor.submit(fetch_and_parse_page, task[0], task[1]): task for task in tasks_to_run}
        
        # Processa os resultados à medida que são concluídos para exibir o progresso
        for i, future in enumerate(as_completed(future_to_task), 1):
            result = future.result()
            if result:
                unordered_results.append(result)
            logger.info(f"Progresso: {i}/{len(tasks_to_run)} páginas coletadas.")
            
    # FASE 3: Organização e Geração do Relatório
    logger.info("Coleta de dados finalizada. Organizando os resultados...")
    unordered_results.sort(key=lambda x: x[0])
    
    all_books_data = []
    for page_num, page_data in unordered_results:
        if page_data:
            all_books_data.extend(page_data)

    logger.info("Gerando o arquivo Excel formatado...")
    colunas = ['Nome', 'Preço', 'URL']
    df = pd.DataFrame(all_books_data, columns=colunas)

    output_filename = 'Itens.xlsx'
    
    # Utiliza o ExcelWriter para ter controle sobre a formatação do arquivo final
    try:
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Produtos')

            # Acessa a planilha para aplicar estilos
            worksheet = writer.sheets['Produtos']

            # Define e aplica o formato de moeda (£) na coluna 'B' (Preço)
            currency_format = '£#,##0.00'
            for cell in worksheet['B'][1:]: # O slice [1:] pula a célula do cabeçalho
                cell.number_format = currency_format

        logger.info(f"Arquivo '{output_filename}' criado com sucesso!")
        
    except Exception as e:
        logger.critical(f"Falha CRÍTICA ao gerar o arquivo Excel: {e}")


if __name__ == "__main__":
    scrape_all_books()