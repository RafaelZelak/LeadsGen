import requests
from datetime import datetime, timedelta
from typing import Dict, Any
from flask import current_app
from .config import BITRIX_WEBHOOK_URL, API_METHOD

class Bitrix24Service:
    @staticmethod
    def format_company_data(company_data: Dict[str, Any], user_group: str) -> Dict[str, Any]:
        """Format company data according to Bitrix24 requirements"""
        # Format dates in Bitrix24 format
        now = datetime.now()
        begin_date = now.strftime("%Y-%m-%dT03:00:00+03:00")
        close_date = (now + timedelta(days=7)).strftime("%Y-%m-%dT03:00:00+03:00")

        # Log incoming data
        current_app.logger.debug(f"Formatting company data for group {user_group}: {company_data}")

        # Define configurações baseadas no grupo
        spa_configs = {
            "Acessórias": {
                "entityTypeId": 187,
                "categoryId": 171,
                "stageId": "DT187_171:NEW",
                "custom_fields": {
                    "company_name": "ufCrm25_1737492364136",
                    "fantasy_name": "ufCrm25_1737492376688",
                    "phone1": "ufCrm25_1737492383384",
                    "phone2": "ufCrm25_1737492391720",
                    "cnpj": "ufCrm25_1737492411713",
                    "value": "ufCrm25_1737492436546",
                    "partners": "ufCrm25_1737492445602",
                    "address": "ufCrm25_1737492452850",
                    "origin": "ufCrm25_1737492460899"
                }
            },
            "BestDoctors": {
                "entityTypeId": 180,
                "categoryId": 167,
                "stageId": "DT180_167:NEW",
                "custom_fields": {
                    "address": "ufCrm27_1737116815834",
                    "phone1": "ufCrm27_1737116879588",
                    "phone2": "ufCrm27_1737116892085",
                    "fantasy_name": "ufCrm27_1737116513433",
                    "cnpj": "ufCrm27_1737116548723",
                    "company_name": "ufCrm27_1737116578139",
                    "partners": "ufCrm27_1737116592547",
                    "value": "ufCrm27_1737116612860",
                    "email": "ufCrm27_1709126258987",
                    "origin": "ufCrm27_1737402187910"
                }
            },
            "Sittax": {
                "entityTypeId": 158,
                "categoryId": 169,
                "stageId": "DT158_169:NEW",
                "custom_fields": {
                    "company_name": "ufCrm5_1737545372279",
                    "cnpj": "ufCrm5_1737545379350",
                    "fantasy_name": "ufCrm5_1737545397702",
                    "phone1": "ufCrm5_1737545408782",
                    "phone2": "ufCrm5_1737545417639",
                    "partners": "ufCrm5_1737545432375",
                    "address": "ufCrm5_1737545585604",
                    "origin": "ufCrm5_1737545455607",
                    "value": "ufCrm5_1737545593714"
                }
            }
        }

        if user_group not in spa_configs:
            raise ValueError(f"Grupo não suportado: {user_group}")

        config = spa_configs[user_group]
        custom_fields = config["custom_fields"]

        # Construir o payload exatamente como no exemplo que funciona
        payload = {
            "entityTypeId": config["entityTypeId"],
            "fields": {
                # Campos principais
                "title": company_data.get("fantasy_name", ""),
                "stageId": company_data.get("stageId", config["stageId"]),
                "categoryId": company_data.get("categoryId", config["categoryId"]),
                "assignedById": company_data.get("assignedById", 629),  # Usar o valor do request se disponível
                "createdBy": 629,     # Forçar criação pelo usuário "Automações"

                # Campos obrigatórios identificados
                "opened": "N",
                "begindate": begin_date,
                "closedate": close_date,
                "currencyId": "BRL",
                "opportunity": 0,
                "isManualOpportunity": "N",
                "sourceId": "CALL",

                # Campos com valores padrão
                "companyId": 0,
                "contactId": 0,
                "mycompanyId": 0,
                "taxValue": 0,
                "taxValueAccount": 0,
                "accountCurrencyId": "BRL",
                "opportunityAccount": 0,
                "webformId": 0,

                # Campos personalizados
                custom_fields["address"]: f"{company_data.get('address', '')}|;|4705" if user_group == "Sittax" else (f"{company_data.get('address', '')}|;|4725" if "ufCrm27" in custom_fields["address"] else company_data.get('address', '')),
                custom_fields["phone1"]: company_data.get('phone1', ''),
                custom_fields["phone2"]: company_data.get('phone2', ''),
                custom_fields["fantasy_name"]: company_data.get('fantasy_name', ''),
                custom_fields["cnpj"]: company_data.get('cnpj', ''),
                custom_fields["company_name"]: company_data.get('company_name', ''),
                custom_fields["partners"]: company_data.get('partners', ''),
                custom_fields["value"]: f"{str(company_data.get('capitalSocial', '0')).replace(',', '').replace('.', '')}|BRL",
            }
        }

        # Log do payload final
        current_app.logger.info(f"Payload final para o Bitrix: {payload}")

        # Adicionar campos específicos dependendo do grupo
        if "email" in custom_fields:
            payload["fields"][custom_fields["email"]] = company_data.get('email', '')
        if "origin" in custom_fields:
            payload["fields"][custom_fields["origin"]] = "Automação Lead"

        return payload

    @staticmethod
    def send_to_bitrix(company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send company data to Bitrix24"""
        try:
            # Get user group
            user_group = company_data.get('group')
            if not user_group:
                raise ValueError("Grupo do usuário não especificado")

            current_app.logger.info(f"User group: {user_group}")

            # Format data according to user's group
            payload = Bitrix24Service.format_company_data(company_data, user_group)

            # Construct URL with trailing slash
            url = f"{BITRIX_WEBHOOK_URL}{API_METHOD}/"

            current_app.logger.info("=== Request Details ===")
            current_app.logger.info(f"Final URL: {url}")
            current_app.logger.info(f"Final payload being sent: {payload}")

            # Make the request
            response = requests.post(url, json=payload)
            response.raise_for_status()

            current_app.logger.info("=== Response Details ===")
            current_app.logger.info(f"Response Status Code: {response.status_code}")
            current_app.logger.info(f"Response Content: {response.text}")

            result = response.json()

            # Check if we need to update the stage
            if response.status_code == 200 and 'result' in result:
                item_id = result['result'].get('item', {}).get('id')
                if item_id:
                    current_app.logger.info(f"Card created successfully with ID: {item_id}")

                    # Atualizar configurações adicionais se necessário
                    update_method = "crm.item.update"
                    update_payload = {
                        "entityTypeId": payload["entityTypeId"],
                        "id": item_id,
                        "fields": {
                            "stageId": payload["fields"]["stageId"]
                        }
                    }
                    update_response = requests.post(f"{BITRIX_WEBHOOK_URL}{update_method}/", json=update_payload)
                    current_app.logger.info(f"Stage update response: {update_response.json()}")

            return {
                "success": True,
                "data": result
            }

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Request Exception: {str(e)}")
            return {
                "success": False,
                "error": f"Request to Bitrix24 failed: {str(e)}"
            }
        except Exception as e:
            current_app.logger.error(f"Unexpected error: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    @staticmethod
    def check_cnpj_exists(cnpj: str, user_group: str) -> bool:
        """Check if CNPJ exists in Bitrix24 for the specific group"""
        try:
            # Define configurações baseadas no grupo
            spa_configs = {
                "Acessórias": {
                    "entityTypeId": 187,
                    "cnpj_field": "ufCrm25_1737492411713"
                },
                "BestDoctors": {
                    "entityTypeId": 180,
                    "cnpj_field": "ufCrm27_1737116548723"
                },
                "Sittax": {
                    "entityTypeId": 158,
                    "cnpj_field": "ufCrm5_1737545379350"
                }
            }

            if user_group not in spa_configs:
                raise ValueError(f"Grupo não suportado: {user_group}")

            config = spa_configs[user_group]

            # Construir o filtro para buscar pelo CNPJ
            filter_payload = {
                "entityTypeId": config["entityTypeId"],
                "filter": {
                    config["cnpj_field"]: cnpj
                }
            }

            # Fazer a requisição para o Bitrix
            url = f"{BITRIX_WEBHOOK_URL}crm.item.list/"
            response = requests.post(url, json=filter_payload)
            response.raise_for_status()

            result = response.json()

            # Se encontrou algum item com este CNPJ, retorna True
            return len(result.get('result', {}).get('items', [])) > 0

        except Exception as e:
            current_app.logger.error(f"Erro ao verificar CNPJ no Bitrix: {str(e)}")
            return False

    @staticmethod
    def check_multiple_cnpjs(cnpjs: list, user_group: str) -> Dict[str, bool]:
        """Check multiple CNPJs at once in Bitrix24"""
        try:
            # Define configurações baseadas no grupo
            spa_configs = {
                "Acessórias": {
                    "entityTypeId": 187,
                    "cnpj_field": "ufCrm25_1737492411713",
                    "categories": {
                        "SDR": 145,
                        "LDR": 171
                    }
                },
                "BestDoctors": {
                    "entityTypeId": 180,
                    "cnpj_field": "ufCrm27_1737116548723",
                    "categories": {
                        "SDR": 149,
                        "LDR": 167
                    }
                },
                "Sittax": {
                    "entityTypeId": 158,
                    "cnpj_field": "ufCrm5_1737545379350",
                    "categories": {
                        "SDR": 159,
                        "LDR": 169
                    }
                }
            }

            if user_group not in spa_configs:
                raise ValueError(f"Grupo não suportado: {user_group}")

            config = spa_configs[user_group]

            # Limpar os CNPJs para garantir formato consistente
            formatted_cnpjs = [cnpj.replace('.', '').replace('/', '').replace('-', '') for cnpj in cnpjs]

            current_app.logger.info(f"Verificando CNPJs formatados: {formatted_cnpjs} para o grupo {user_group}")

            # Construir o filtro para buscar pelos CNPJs em ambos os pipelines
            filter_payload = {
                "entityTypeId": config["entityTypeId"],
                "filter": {
                    "categoryId": list(config["categories"].values()),  # Busca em SDR e LDR
                    config["cnpj_field"]: formatted_cnpjs
                },
                "select": ["*"]
            }

            current_app.logger.info(f"Payload da requisição: {filter_payload}")

            # Fazer a requisição para o Bitrix
            url = f"{BITRIX_WEBHOOK_URL}crm.item.list/"
            response = requests.post(url, json=filter_payload)
            response.raise_for_status()

            result = response.json()
            current_app.logger.info(f"Resposta do Bitrix: {result}")

            # Extrair CNPJs existentes e formatá-los da mesma maneira
            existing_cnpjs = set()
            for item in result.get('result', {}).get('items', []):
                if config["cnpj_field"] in item:
                    cnpj = item[config["cnpj_field"]]
                    if cnpj:  # Verifica se o CNPJ não é vazio
                        formatted_cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')
                        existing_cnpjs.add(formatted_cnpj)

            current_app.logger.info(f"CNPJs encontrados no Bitrix: {existing_cnpjs}")

            # Retorna um dicionário com o status de cada CNPJ
            result_map = {cnpj: cnpj.replace('.', '').replace('/', '').replace('-', '') in existing_cnpjs for cnpj in cnpjs}
            current_app.logger.info(f"Mapa de resultados: {result_map}")

            return result_map

        except Exception as e:
            current_app.logger.error(f"Erro ao verificar CNPJs no Bitrix: {str(e)}")
            current_app.logger.error(f"Detalhes do erro: {str(e.__class__.__name__)}: {str(e)}")
            return {cnpj: False for cnpj in cnpjs}