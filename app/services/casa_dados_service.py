import cloudscraper
import requests
import aiohttp
import asyncio
from flask import current_app
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CasaDadosService:
    API_URL = "https://api.casadosdados.com.br/v2/public/cnpj/search"
    BRASIL_API_URL = "https://brasilapi.com.br/api/cnpj/v1"
    scraper = None

    @classmethod
    def get_scraper(cls):
        if cls.scraper is None:
            cls.scraper = cloudscraper.create_scraper()
            logger.info("Scraper criado com sucesso.")
        return cls.scraper

    @staticmethod
    async def fetch_brasil_api_data(session, cnpj):
        cnpj_clean = ''.join(filter(str.isdigit, cnpj))
        url = f"{CasaDadosService.BRASIL_API_URL}/{cnpj_clean}"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return cnpj, await response.json()
                else:
                    logger.warning(f"Erro {response.status} na Brasil API para o CNPJ {cnpj_clean}")
        except Exception as e:
            logger.error(f"Erro ao buscar dados da Brasil API para o CNPJ {cnpj}: {e}")
        return cnpj, None

    @staticmethod
    async def batch_get_brasil_api_data(cnpjs):
        async with aiohttp.ClientSession() as session:
            tasks = [CasaDadosService.fetch_brasil_api_data(session, cnpj) for cnpj in cnpjs]
            results = await asyncio.gather(*tasks)
        return dict(results)

    @staticmethod
    def search_companies(search_term, page=1, filters=None, type_query=None):
        if filters is None:
            filters = {}

        type_query = type_query or 'termo'
        query_value = [search_term]

        payload = {
            "query": {
                "termo": [search_term] if type_query == "termo" else [],
                "atividade_principal": query_value if type_query == "cnae" else [],
                "natureza_juridica": [],
                "uf": [filters.get('state', '').strip().upper()] if filters.get('state') else [],
                "municipio": [filters.get('city', '').strip().upper()] if filters.get('city') else [],
                "bairro": [filters.get('neighborhood', '').strip().upper()] if filters.get('neighborhood') else [],
                "situacao_cadastral": "ATIVA",
                "cep": [],
                "ddd": []
            },
            "range_quera": {
                "data_abertura": {"lte": None, "gte": None},
                "capital_social": {"lte": None, "gte": None}
            },
            "extras": {
                "somente_mei": False,
                "excluir_mei": False,
                "com_email": False,
                "incluir_atividade_secundaria": False,
                "com_contato_telefonico": False,
                "somente_fixo": False,
                "somente_celular": False,
                "somente_matriz": False,
                "somente_filial": False
            },
            "page": page
        }

        logger.info(f"Enviando payload para a API Casa dos Dados: {payload}")

        try:
            scraper = CasaDadosService.get_scraper()
            response = scraper.post(CasaDadosService.API_URL, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

            cnpjs = [company.get('cnpj', '') for company in data.get('data', {}).get('cnpj', [])[:10]]
            brasil_api_results = asyncio.run(CasaDadosService.batch_get_brasil_api_data(cnpjs))

            companies = []
            for company in data.get('data', {}).get('cnpj', [])[:10]:
                brasil_api_data = brasil_api_results.get(company.get('cnpj', ''), None)

                base_company = {
                    'id': company.get('cnpj', ''),
                    'razaoSocial': company.get('razao_social', ''),
                    'nomeFantasia': company.get('nome_fantasia') or company.get('razao_social', ''),
                    'cnpj': company.get('cnpj', ''),
                    'status': company.get('situacao_cadastral', ''),
                    'telefone1': brasil_api_data.get('ddd_telefone_1', '') if brasil_api_data else company.get('ddd_telefone_1', ''),
                    'telefone2': brasil_api_data.get('ddd_telefone_2', '') if brasil_api_data else company.get('ddd_telefone_2', ''),
                    'email': brasil_api_data.get('email', '') if brasil_api_data else '',
                    'capitalSocial': str(brasil_api_data.get('capital_social', company.get('capital_social', ''))),
                    'socios': [
                        f"{socio.get('nome_socio', '')} ({socio.get('qualificacao_socio', '')})"
                        for socio in brasil_api_data.get('qsa', [])
                    ],
                    'address': f"{company.get('logradouro', '')}, {company.get('numero', '')}{' - ' + company.get('complemento', '') if company.get('complemento') else ''} - {company.get('bairro', '')} - {company.get('municipio', '')}/{company.get('uf', '')}".replace('  ', ' ').strip(),
                    'city': company.get('municipio', ''),
                    'state': company.get('uf', ''),
                    'neighborhood': company.get('bairro', ''),
                    'atividadePrincipal': {
                        'codigo': company.get('cnae_fiscal', ''),
                        'descricao': company.get('cnae_fiscal_descricao', '')
                    }
                }
                companies.append(base_company)

            total = data.get('data', {}).get('count', 0)
            total_pages = -(-total // 10)
            logger.info(f"Processamento concluído. Total de empresas encontradas: {total}")

            return {
                'items': companies,
                'total': total,
                'pages': total_pages,
                'current_page': page
            }
        except Exception as e:
            logger.error(f"Erro ao processar a requisição: {str(e)}")
            raise ValueError(f"Falha ao buscar dados da Casa dos Dados: {str(e)}")
