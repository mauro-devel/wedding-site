import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class Config:
    WEDDING_DATE = os.environ.get('WEDDING_DATE') or '2027-04-03T15:00:00+01:00'
    CEREMONY_MAPS_URL = os.environ.get('CEREMONY_MAPS_URL') or 'https://www.google.com/maps/place//data=!4m2!3m1!1s0xd2464e6c2a4163b:0xfde6dd68a1ab3e6c?sa=X&ved=1t:8290&ictx=111'
    PARTY_MAPS_URL = os.environ.get('PARTY_MAPS_URL') or 'https://www.google.com/maps/place//data=!4m2!3m1!1s0xd248faa9a378119:0x5681a6a4421c41ba?sa=X&ved=1t:8290&ictx=111'
    WEDDING_NIB = os.environ.get('WEDDING_NIB') or '00100006567652000172'
    WEDDING_IBAN = os.environ.get('WEDDING_IBAN') or 'PT50001000006567652000172'
    WEDDING_SWIFT = os.environ.get('WEDDING_SWIFT') or 'BBPIPTPL'
    PLAYLIST_URL = os.environ.get('PLAYLIST_URL') or 'https://open.spotify.com/playlist/2zLzo2KsZpMon4nZuyb5Ip?si=4ef1495c3d7b44f8'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BABEL_DEFAULT_LOCALE = 'es'
    BABEL_TRANSLATION_DIRECTORIES = str(BASE_DIR / 'app' / 'translations')
    LANGUAGES = {
        'es': 'Español',
        'pt_PT': 'Português'
    }

    UPLOAD_FOLDER = BASE_DIR / 'app' / 'static' / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{BASE_DIR / "wedding.db"}'
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{BASE_DIR / "data" / "wedding.db"}'
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in production