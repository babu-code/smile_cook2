import os

class Config:
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ERROR_MESSAGE_KEY = 'message'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    UPLOADED_IMAGES_DEST = 'static/images'
    ALLOWED_FILE_EXTENSIONS =[ '.png', '.jpg', '.jpeg', '.gif']
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 10*60
    RATELIMIT_HEADERS_ENABLED = True

class DevelopmentConfig(Config):
    DEBUG=True
    SECRET_KEY = 'fdb82ec5ba04b1656c4a00ba0d856d96'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://tony:1234@localhost/smile_cook2'
    MAILGUN_API_KEY = 'e32fd32058bda5a6f902b35da64c128b-8c8e5529-423025de'

class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
class StagingConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')