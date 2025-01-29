import time
import json
import cloudscraper
from datetime import datetime

# Configuração inicial
INTERVALO_VERIFICACAO = 3600  # Tempo entre verificações em segundos (1 hora)
API_URL = "https://api.casadosdados.com.br/v2/public/cnpj/search"
HEADERS = {"Content-Type": "application/json"}
ULTIMOS_CNPJS = set()
CNAE_CONTABILIDADE = "6920601"  # CNAE para contabilidade
MUNICIPIO = "CURITIBA"
UF = "PR"

def buscar_empresas_por_data():
    """Faz a requisição para a API da Casa dos Dados filtrando pela data de abertura de hoje, CNAE de contabilidade e Curitiba/PR."""
    hoje = datetime.today().strftime("%Y-%m-%d")
    payload = {
        "query": {
            "atividade_principal": [CNAE_CONTABILIDADE],
            "situacao_cadastral": "ATIVA",
            "municipio": [MUNICIPIO],
            "uf": [UF]
        },
        "range_quera": {
            "data_abertura": {
                "gte": f"{hoje}T00:00:00Z",
                "lte": f"{hoje}T23:59:59Z"
            }
        },
        "extras": {
            "somente_mei": False,
            "excluir_mei": False,
            "somente_matriz": False
        },
        "page": 1
    }

    scraper = cloudscraper.create_scraper()
    response = scraper.post(API_URL, headers=HEADERS, json=payload)

    print("Resposta da API:", response.text)  # Depuração

    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                return data["data"]
            else:
                print("Erro: Resposta inesperada da API.")
                return []
        except json.JSONDecodeError:
            print("Erro ao decodificar resposta da API.")
            return []
    else:
        print(f"Erro ao buscar dados: {response.status_code} - {response.text}")
        return []

def verificar_novos_cnpjs():
    """Verifica se há novos CNPJs registrados hoje e exibe as diferenças."""
    global ULTIMOS_CNPJS
    novas_empresas = buscar_empresas_por_data()

    if not isinstance(novas_empresas, list):
        print("Erro: formato de resposta inesperado.")
        return

    novos_cnpjs = {empresa.get("cnpj", "") for empresa in novas_empresas if isinstance(empresa, dict)}
    novos_detectados = novos_cnpjs - ULTIMOS_CNPJS

    if novos_detectados:
        print("Novas empresas encontradas hoje em Curitiba/PR:")
        for cnpj in novos_detectados:
            empresa = next((e for e in novas_empresas if e.get("cnpj") == cnpj), None)
            if empresa:
                print(f"CNPJ: {cnpj} - Nome: {empresa.get('razao_social', 'Desconhecido')} - Data Abertura: {empresa.get('data_abertura', 'Desconhecido')}")
    else:
        print("Nenhuma nova empresa encontrada hoje em Curitiba/PR.")

    ULTIMOS_CNPJS = novos_cnpjs

if __name__ == "__main__":
    while True:
        verificar_novos_cnpjs()
        time.sleep(INTERVALO_VERIFICACAO)
