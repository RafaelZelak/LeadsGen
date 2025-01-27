import requests
from flask import current_app
from app.data import companies

class CompanyService:
    @staticmethod
    def get_companies(page=1, per_page=None, search_term=None, filters=None):
        if per_page is None:
            per_page = current_app.config['COMPANIES_PER_PAGE']

        filtered_companies = companies

        # Apply search
        if search_term:
            search_term = search_term.lower()
            filtered_companies = [
                company for company in filtered_companies
                if search_term in company['razaoSocial'].lower() or
                   search_term in company['nomeFantasia'].lower() or
                   search_term in company['cnpj']
            ]

        # Apply filters
        if filters:
            if filters.get('city'):
                city = filters['city'].lower()
                filtered_companies = [
                    company for company in filtered_companies
                    if city in company['city'].lower()
                ]
            if filters.get('state'):
                state = filters['state'].lower()
                filtered_companies = [
                    company for company in filtered_companies
                    if state in company['state'].lower()
                ]
            if filters.get('neighborhood'):
                neighborhood = filters['neighborhood'].lower()
                filtered_companies = [
                    company for company in filtered_companies
                    if neighborhood in company['neighborhood'].lower()
                ]

        # Calculate pagination
        total = len(filtered_companies)
        total_pages = (total + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page

        return {
            'items': filtered_companies[start:end],
            'total': total,
            'pages': total_pages,
            'current_page': page
        }

    @staticmethod
    def send_to_bitrix(company_id):
        company = next((c for c in companies if c['id'] == str(company_id)), None)
        if not company:
            raise ValueError(f"Company with id {company_id} not found")

        webhook_url = current_app.config['BITRIX_WEBHOOK_URL']
        if not webhook_url:
            raise ValueError("Bitrix webhook URL not configured")

        # Prepare data for Bitrix
        data = {
            'fields': {
                'TITLE': company['razaoSocial'],
                'COMPANY_TYPE': 'CUSTOMER',
                'INDUSTRY': 'OTHER',
                'PHONE': [{'VALUE': company['telefone1'], 'VALUE_TYPE': 'WORK'}],
                'EMAIL': [{'VALUE': company['email'], 'VALUE_TYPE': 'WORK'}],
                'ADDRESS': company['address'],
                'ADDRESS_CITY': company['city'],
                'ADDRESS_REGION': company['state'],
            }
        }

        # Send to Bitrix
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()

        return response.json()