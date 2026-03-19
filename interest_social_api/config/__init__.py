import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'interest-social-api-secret-key-2024'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-2024'
    JWT_EXPIRATION_HOURS = 24 * 7
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(basedir), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(basedir), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
