import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    """Configurações base da aplicação."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'voce-precisa-mudar-isso-para-algo-seguro'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'expenses.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False