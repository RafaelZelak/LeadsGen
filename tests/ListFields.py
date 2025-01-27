"""
ListFields.py - Listador de Cards do Smart Process

Este script lista todos os cards disponíveis em pipelines específicos (SDR e LDR)
de cada Smart Process, incluindo todos os seus campos e valores.

Funcionalidades principais:
1. Busca cards nos pipelines SDR e LDR de um SPA específico
2. Lista todos os campos disponíveis para cada card
3. Organiza os campos por tipo (padrão/personalizado)
4. Mostra o valor atual de cada campo

Como usar:
1. Execute o script:
   python ListFields.py
"""
import requests
from typing import Dict, Any, List
import json
import os

# Endpoint e chave de autenticação
BITRIX_WEBHOOK_URL = "https://setup.bitrix24.com.br/rest/629/c0q6gqm7og1bs91k/"

# Configurações dos SPAs
SPA_CONFIGS = {
    "Acessórias": {
        "entityTypeId": 187,
        "name": "Acessórias",
        "categories": {
            "SDR": 171,  # Pipeline SDR
            "LDR": 172   # Pipeline LDR
        },
        "fields": {
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
        "name": "Best Doctors",
        "categories": {
            "SDR": 167,  # Pipeline SDR
            "LDR": 149   # Pipeline LDR
        },
        "fields": {
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
        "name": "Sittax",
        "categories": {
            "SDR": 169,  # Pipeline SDR
            "LDR": 170   # Pipeline LDR
        },
        "fields": {
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

def get_all_cards(entity_type_id: int, categories: Dict[str, int], fields: Dict[str, str]) -> List[Dict[str, Any]]:
    """Busca todos os cards de um SPA específico nos pipelines SDR e LDR"""
    method = "crm.item.list"
    cards = []
    start = 0

    # Criar lista de campos para selecionar
    select = ["*"] + list(fields.values())

    # Lista de categorias para buscar
    category_ids = list(categories.values())

    while True:
        payload = {
            "entityTypeId": entity_type_id,
            "select": select,
            "filter": {
                "categoryId": category_ids
            },
            "start": start
        }

        try:
            response = requests.post(f"{BITRIX_WEBHOOK_URL}{method}/", json=payload)
            response.raise_for_status()
            data = response.json()

            items = data.get('result', {}).get('items', [])
            if not items:
                break

            cards.extend(items)
            start += 50  # Bitrix usa paginação de 50 em 50

            print(f"Carregados {len(cards)} cards...")

        except Exception as e:
            print(f"Erro ao buscar cards: {e}")
            break

    return cards

def format_card_fields(card: Dict[str, Any]) -> Dict[str, Any]:
    """Formata os campos de um card"""
    formatted = {
        'id': card.get('id'),
        'title': card.get('title'),
        'categoryId': card.get('categoryId'),
        'stageId': card.get('stageId'),
        'standard_fields': {},
        'custom_fields': {}
    }

    # Campos que queremos ignorar na saída para manter o JSON limpo
    ignore_fields = {
        'id', 'title', 'categoryId', 'stageId', 'fields'
    }

    # Processar campos padrão
    for field, value in card.items():
        if field not in ignore_fields:
            if field.startswith('uf'):
                formatted['custom_fields'][field] = value
            else:
                formatted['standard_fields'][field] = value

    return formatted

def save_to_file(spa_name: str, cards: List[Dict[str, Any]]):
    """Salva os resultados em um arquivo JSON"""
    # Criar pasta de testes se não existir
    test_dir = "tests"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    filename = os.path.join(test_dir, f"{spa_name}_cards.json")

    formatted_cards = [format_card_fields(card) for card in cards]

    # Adicionar informações extras
    output = {
        "spa_name": spa_name,
        "total_cards": len(formatted_cards),
        "cards": formatted_cards
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nDados salvos em {filename}")
    print(f"Total de cards formatados: {len(formatted_cards)}")

def list_spa_cards():
    """Função principal para listar cards de um SPA"""
    print("SPAs disponíveis:")
    for i, spa in enumerate(SPA_CONFIGS.keys(), 1):
        print(f"{i}. {spa}")

    while True:
        try:
            choice = int(input("\nEscolha o número do SPA (ou 0 para sair): "))
            if choice == 0:
                return

            if 1 <= choice <= len(SPA_CONFIGS):
                spa_name = list(SPA_CONFIGS.keys())[choice - 1]
                spa_config = SPA_CONFIGS[spa_name]
                break
            else:
                print("Opção inválida!")
        except ValueError:
            print("Por favor, digite um número válido!")

    print(f"\nBuscando cards do SPA: {spa_config['name']}")
    cards = get_all_cards(spa_config['entityTypeId'], spa_config['categories'], spa_config['fields'])

    if cards:
        print(f"\nTotal de cards encontrados: {len(cards)}")
        save_to_file(spa_name, cards)
    else:
        print("Nenhum card encontrado!")

if __name__ == "__main__":
    list_spa_cards()