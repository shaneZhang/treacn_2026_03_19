import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '../app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your-secret-key-here-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    UPLOAD_FOLDER = os.path.join(basedir, '../uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
