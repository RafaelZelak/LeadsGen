from decouple import Config, RepositoryEnv

# Initialize config from .env
env_config = Config(RepositoryEnv('.env'))

# Bitrix24 API Configuration
BITRIX_WEBHOOK_URL = "https://setup.bitrix24.com.br/rest/629/c0q6gqm7og1bs91k/"
API_METHOD = "crm.item.add"

# SPA Configurations by Group
SPA_CONFIGS = {
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
            "fantasy_name": "ufCrm5_1737545397702",
            "phone1": "ufCrm5_1737545408782",
            "phone2": "ufCrm5_1737545417639",
            "cnpj": "ufCrm5_1737545379350",
            "value": "ufCrm5_1737545593714",
            "partners": "ufCrm5_1737545432375",
            "address": "ufCrm5_1737545585604",
            "origin": "ufCrm5_1737545455607"
        }
    }
}

# Default Field Values
DEFAULT_FIELDS = {
    "opened": "N",
    "currencyId": "BRL",
    "opportunity": 0,
    "isManualOpportunity": "N",
    "sourceId": "CALL",
    "companyId": 0,
    "contactId": 0,
    "mycompanyId": 0,
    "taxValue": 0,
    "taxValueAccount": 0,
    "accountCurrencyId": "BRL",
    "opportunityAccount": 0,
    "webformId": 0
}