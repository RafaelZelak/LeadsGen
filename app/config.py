from decouple import config

class Config:
    # Flask configuration
    SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')

    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = 'flask_session/'
    SESSION_FILE_THRESHOLD = 500
    SESSION_FILE_MODE = 384
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds

    # API configuration
    BITRIX_WEBHOOK_URL = config('BITRIX_WEBHOOK_URL', default="")

    # Pagination
    COMPANIES_PER_PAGE = 5
