from flask import Blueprint, render_template, request, jsonify, session, current_app
from app.services.casa_dados_service import CasaDadosService
from app.routes.auth_routes import login_required
from app.services.auth_service import AuthService
from app.services.bitrix import Bitrix24Service
import os
import json

company_bp = Blueprint('company', __name__)

@company_bp.route('/')
@login_required
def index():
    display_name = AuthService.get_user_display_name()
    context = {
        'user_name': display_name
    }

    return render_template('index.html', **context)

@company_bp.route('/api/companies')
@login_required
def get_companies():
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '').strip()
    type_query = request.args.get('typeQuery', 'termo')  # Pega o valor de typeQuery ou usa 'termo' por padrão

    # Se não houver termo de busca, retorna lista vazia
    if not search_term:
        return jsonify({
            'items': [],
            'total': 0,
            'pages': 0,
            'current_page': page
        })

    # Pega os filtros da query string
    filters = {
        'city': request.args.get('city', '').strip(),
        'state': request.args.get('state', '').strip(),
        'neighborhood': request.args.get('neighborhood', '').strip()
    }

    try:
        # Passa o type_query para a função search_companies
        result = CasaDadosService.search_companies(
            search_term=search_term,
            page=page,
            filters=filters,
            type_query=type_query  # Passando o tipo de busca
        )
        print(f"\n\n\n{result}\n\n\n")
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/api/companies/<string:company_id>/send-to-bitrix', methods=['POST'])
@login_required
def send_to_bitrix(company_id):
    try:
        # Log raw request data
        current_app.logger.info("=== Request Information ===")
        current_app.logger.info(f"Request Method: {request.method}")
        current_app.logger.info(f"Content-Type: {request.headers.get('Content-Type')}")
        current_app.logger.info(f"Raw Data: {request.get_data()}")

        # Get and validate company data from request
        company_data = request.get_json(force=True)  # force=True to try parsing even if content-type is wrong

        current_app.logger.info(f"Parsed company_data: {company_data}")
        current_app.logger.info("=== End Request Information ===")

        if not company_data:
            current_app.logger.error("No company data provided in request")
            return jsonify({'error': "Company data is required"}), 400

        # Send to Bitrix24
        result = Bitrix24Service.send_to_bitrix(company_data)

        if not result['success']:
            current_app.logger.error(f"Failed to send to Bitrix: {result['error']}")
            return jsonify({'error': result['error']}), 400

        current_app.logger.info(f"Successfully sent company {company_id} to Bitrix")
        return jsonify({'message': 'Company sent to Bitrix successfully', 'data': result['data']})
    except ValueError as e:
        current_app.logger.error(f"ValueError while sending to Bitrix: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error while sending to Bitrix: {str(e)}")
        return jsonify({'error': f"Erro ao enviar para o Bitrix: {str(e)}"}), 500

@company_bp.route('/api/companies/check-bitrix', methods=['POST'])
@login_required
def check_cnpjs_in_bitrix():
    try:
        # Get CNPJs and group from request
        data = request.get_json()
        if not data or 'cnpjs' not in data or 'group' not in data:
            return jsonify({'error': 'Lista de CNPJs e grupo não fornecidos'}), 400

        # Log para debug
        current_app.logger.info(f"Verificando CNPJs: {data['cnpjs']} para o grupo: {data['group']}")

        # Check CNPJs in Bitrix using the provided group
        exists_map = Bitrix24Service.check_multiple_cnpjs(data['cnpjs'], data['group'])

        return jsonify({
            'results': exists_map
        })
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar CNPJs no Bitrix: {str(e)}")
        return jsonify({'error': str(e)}), 500

@company_bp.route('/api/cnaes', methods=['GET'])
@login_required
def get_cnaes():
    try:
        # Define o caminho correto para o arquivo cnaes.json
        cnaes_file_path = os.path.join(current_app.root_path, 'routes', '..', 'data', 'cnaes.json')

        # Verifica se o arquivo existe
        if not os.path.exists(cnaes_file_path):
            current_app.logger.error(f"Arquivo CNAEs não encontrado em: {cnaes_file_path}")
            return jsonify({'error': 'Arquivo CNAEs não encontrado'}), 404

        # Lê o arquivo JSON
        with open(cnaes_file_path, 'r', encoding='utf-8') as f:
            cnaes_data = json.load(f)

        # Retorna os dados do CNAE como JSON
        return jsonify(cnaes_data)

    except Exception as e:
        current_app.logger.error(f"Erro ao ler o arquivo CNAEs: {str(e)}")
        return jsonify({'error': f"Erro ao ler o arquivo CNAEs: {str(e)}"}), 500