import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Configurações base da aplicação."""
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # --- LÓGICA DE CONEXÃO COM BANCO DE DADOS ---

    # Variáveis de ambiente do Google Cloud SQL (usadas no Cloud Run/App Engine)
    db_connection_name = os.environ.get('INSTANCE_CONNECTION_NAME')
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASS')
    db_name = os.environ.get('DB_NAME')

    # Variável genérica de URL (Ex: Render, Railway, Heroku)
    database_url = os.environ.get('DATABASE_URL')

    if db_connection_name:
        # --- CENÁRIO 1: Google Cloud SQL (PostgreSQL via Unix Socket) ---
        # Usa o Unix Socket para conexão eficiente no Google Cloud
        # Requer que as variáveis DB_USER/PASS/NAME estejam setadas no ambiente
        SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{db_connection_name}"

    elif database_url:
        # --- CENÁRIO 2: URL Direta (Outros Clouds) ---
        # Corrige o prefixo 'postgres://' se necessário (para compatibilidade com Psycopg2)
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url

    else:
        # --- CENÁRIO 3: Desenvolvimento Local (SQLite) ---
        # Usado quando nenhuma variável de ambiente de Cloud está presente
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'expenses.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False