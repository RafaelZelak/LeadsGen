from flask import Flask
from flask_cors import CORS
from flask_session import Session
from decouple import Config, RepositoryEnv
from app.config import Config as AppConfig

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(AppConfig)

    # Load environment variables from .env
    env_config = Config(RepositoryEnv('.env'))
    app.config['BITRIX_WEBHOOK_URL'] = env_config('BITRIX_WEBHOOK_URL', default="https://setup.bitrix24.com.br/rest/301/gyer7nrqxonhk609")

    # Initialize Flask-Session
    Session(app)

    # Clear template cache
    app.jinja_env.cache = {}

    # Initialize extensions
    CORS(app)

    # Register blueprints
    from app.routes.company_routes import company_bp
    from app.routes.auth_routes import auth_bp

    app.register_blueprint(company_bp)
    app.register_blueprint(auth_bp)

    return app