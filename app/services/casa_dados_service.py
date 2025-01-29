import cloudscraper
import requests
from flask import current_app
import logging

class CasaDadosService:
    API_URL = "https://api.casadosdados.com.br/v2/public/cnpj/search"
    BRASIL_API_URL = "https://brasilapi.com.br/api/cnpj/v1"
    scraper = None

    @classmethod
    def get_scraper(cls):
        if cls.scraper is None:
            cls.scraper = cloudscraper.create_scraper()
        return cls.scraper

    @staticmethod
    def get_brasil_api_data(cnpj):
        try:
            # Remove caracteres especiais do CNPJ
            cnpj_clean = ''.join(filter(str.isdigit, cnpj))
            response = requests.get(f"{CasaDadosService.BRASIL_API_URL}/{cnpj_clean}")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching data from Brasil API for CNPJ {cnpj}: {e}")
        return None

    @staticmethod
    def merge_company_data(casa_dados_company, brasil_api_data):
        if not brasil_api_data:
            return casa_dados_company

        # Formata os sócios da Brasil API
        socios = []
        for socio in brasil_api_data.get('qsa', []):
            socio_info = f"{socio.get('nome_socio')} ({socio.get('qualificacao_socio')})"
            socios.append(socio_info)

        # Formata o capital social
        capital_social = brasil_api_data.get('capital_social', '')
        if capital_social:
            try:
                capital_float = float(capital_social)
                capital_social = f"R$ {capital_float:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
            except:
                pass

        # Formata o endereço completo
        tipo_logradouro = brasil_api_data.get('descricao_tipo_de_logradouro', '')
        logradouro = brasil_api_data.get('logradouro', '')
        numero = brasil_api_data.get('numero', '')
        complemento = brasil_api_data.get('complemento', '')
        bairro = brasil_api_data.get('bairro', '')
        municipio = brasil_api_data.get('municipio', '')
        uf = brasil_api_data.get('uf', '')
        cep = brasil_api_data.get('cep', '')

        # Monta o endereço completo
        endereco_partes = []

        # Adiciona logradouro com tipo
        if tipo_logradouro and logradouro:
            endereco_partes.append(f"{tipo_logradouro} {logradouro}")
        elif logradouro:
            endereco_partes.append(logradouro)

        # Adiciona número
        if numero and endereco_partes:
            endereco_partes[-1] = f"{endereco_partes[-1]}, {numero}"

        # Adiciona complemento
        if complemento:
            endereco_partes.append(complemento)

        # Adiciona bairro
        if bairro:
            endereco_partes.append(bairro)

        # Adiciona cidade/UF
        if municipio and uf:
            endereco_partes.append(f"{municipio}/{uf}")

        # Adiciona CEP
        if cep:
            endereco_partes.append(f"CEP: {cep}")

        # Junta todas as partes com " - "
        endereco_completo = " - ".join(endereco_partes)

        # Formata os telefones
        telefone1 = brasil_api_data.get('ddd_telefone_1', '').strip()
        if telefone1:
            telefone1 = f"({telefone1[:2]}) {telefone1[2:]}"

        telefone2 = brasil_api_data.get('ddd_telefone_2', '').strip()
        if telefone2:
            telefone2 = f"({telefone2[:2]}) {telefone2[2:]}"

        return {
            'id': casa_dados_company.get('id', ''),
            'razaoSocial': brasil_api_data.get('razao_social', casa_dados_company.get('razaoSocial', '')),
            'nomeFantasia': brasil_api_data.get('nome_fantasia', casa_dados_company.get('nomeFantasia', '')),
            'cnpj': casa_dados_company.get('cnpj', ''),
            'status': brasil_api_data.get('descricao_situacao_cadastral', casa_dados_company.get('status', '')),
            'telefone1': telefone1 or casa_dados_company.get('telefone1', ''),
            'telefone2': telefone2 or casa_dados_company.get('telefone2', ''),
            'email': brasil_api_data.get('email', ''),
            'capitalSocial': capital_social or casa_dados_company.get('capitalSocial', ''),
            'socios': socios,
            'address': endereco_completo or casa_dados_company.get('address', ''),
            'city': brasil_api_data.get('municipio', casa_dados_company.get('city', '')),
            'state': brasil_api_data.get('uf', casa_dados_company.get('state', '')),
            'neighborhood': brasil_api_data.get('bairro', casa_dados_company.get('neighborhood', '')),
            'atividadePrincipal': {
                'codigo': str(brasil_api_data.get('cnae_fiscal', '')),
                'descricao': brasil_api_data.get('cnae_fiscal_descricao', '')
            }
        }

    @staticmethod
    def search_companies(search_term, page=1, filters=None, type_query=None):
        if filters is None:
            filters = {}

        # Se type_query não for enviado, define "termo" como valor padrão
        if not type_query:
            type_query = 'termo'

        # Trata os filtros de localização
        state = filters.get('state', '').strip().upper()
        city = filters.get('city', '').strip().upper()
        neighborhood = filters.get('neighborhood', '').strip().upper()

        # Define a chave de busca com base no type_query
        query_key = "termo" if type_query == "termo" else "atividade_principal"

        # Ajuste do payload para CNAE
        if type_query == 'cnae':
            query_value = [search_term]  # Quando for cnae, enviamos o código diretamente
        else:
            query_value = [search_term]  # Para o tipo 'termo', mantemos o valor do search_term

        payload = {
            "query": {
                "termo": [search_term] if type_query == "termo" else [],
                "atividade_principal": query_value if type_query == "cnae" else [],
                "natureza_juridica": [],
                "uf": [state] if state else [],
                "municipio": [city] if city else [],
                "bairro": [neighborhood] if neighborhood else [],
                "situacao_cadastral": "ATIVA",
                "cep": [],
                "ddd": []
            },
            "range_quera": {
                "data_abertura": {
                    "lte": None,
                    "gte": None
                },
                "capital_social": {
                    "lte": None,
                    "gte": None
                }
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

        # Log de o que está sendo enviado para a API

        try:
            scraper = CasaDadosService.get_scraper()
            response = scraper.post(
                CasaDadosService.API_URL,
                json=payload,
                timeout=60
            )

            response.raise_for_status()
            data = response.json()

            # Log de resposta da API

            companies = []
            for company in data.get('data', {}).get('cnpj', [])[:10]:  # Garante máximo de 10 resultados
                brasil_api_data = CasaDadosService.get_brasil_api_data(company.get('cnpj', ''))

                base_company = {
                    'id': company.get('cnpj', ''),
                    'razaoSocial': company.get('razao_social', ''),
                    'nomeFantasia': company.get('nome_fantasia') or company.get('razao_social', ''),
                    'cnpj': company.get('cnpj', ''),
                    'status': company.get('situacao_cadastral', ''),
                    'telefone1': company.get('ddd_telefone_1', ''),
                    'telefone2': company.get('ddd_telefone_2', ''),
                    'email': '',
                    'capitalSocial': company.get('capital_social', ''),
                    'socios': [],
                    'address': f"{company.get('logradouro', '')}, {company.get('numero', '')}{' - ' + company.get('complemento', '') if company.get('complemento') else ''} - {company.get('bairro', '')} - {company.get('municipio', '')}/{company.get('uf', '')}".replace('  ', ' ').strip(),
                    'city': company.get('municipio', ''),
                    'state': company.get('uf', ''),
                    'neighborhood': company.get('bairro', ''),
                    'atividadePrincipal': {
                        'codigo': company.get('cnae_fiscal', ''),
                        'descricao': company.get('cnae_fiscal_descricao', '')
                    }
                }

                enriched_company = CasaDadosService.merge_company_data(base_company, brasil_api_data)
                companies.append(enriched_company)

            total = data.get('data', {}).get('count', 0)
            total_pages = -(-total // 10)  # Ceiling division

            return {
                'items': companies,
                'total': total,
                'pages': total_pages,
                'current_page': page
            }

        except Exception as e:
            # Log do erro
            print(f"Erro ao processar a requisição: {str(e)}")
            if hasattr(e, 'response'):
                print(f"Conteúdo da resposta de erro: {e.response.text}")
                print(f"Headers da resposta de erro: {e.response.headers}")
            raise ValueError(f"Falha ao buscar dados da Casa dos Dados: {str(e)}")
