import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    APP_ENV = os.environ.get('APP_ENV', 'development')
    SECRET_KEY = os.environ.get('APP_SECRET_KEY', os.urandom(32).hex())
    DEBUG = os.environ.get('APP_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('GUNICORN_BIND_ADDRESS', '0.0.0.0')
    PORT = int(os.environ.get('GUNICORN_BIND_PORT', 5000))
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', os.urandom(32).hex())
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 60))
    
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', os.urandom(16).hex())
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha256'
    SECURITY_PASSWORD_LENGTH = 12
    
    SESSION_COOKIE_SECURE = APP_ENV == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': Config
}

def get_config():
    env = os.environ.get('APP_ENV', 'development')
    return config_by_name.get(env, Config)
