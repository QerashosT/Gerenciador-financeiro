from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
import os

# Inicializa as extensões
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
# Define a view (rota) que o Flask-Login deve redirecionar caso o usuário não esteja logado
login_manager.login_view = 'auth.login'
# Mensagem de "faça o login"
login_manager.login_message = 'Por favor, faça o login para acessar esta página.'
login_manager.login_message_category = 'info'  # Categoria para o flash message


def create_app(config_class=Config):
    """
    Cria e configura uma instância da aplicação Flask (Application Factory).
    """

    # Define os caminhos de templates e static
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(BASE_DIR, 'templates')
    static_dir = os.path.join(BASE_DIR, 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)

    # Inicializa as extensões com o app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Importa e registra os Blueprints
    from project.auth.routes import auth as auth_blueprint
    from project.main.routes import main as main_blueprint
    from project.investments.routes import investments as investments_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint)
    app.register_blueprint(investments_blueprint)

    # Cria as tabelas do banco de dados, se não existirem
    with app.app_context():
        db.create_all()

    return app