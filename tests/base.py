import unittest
from project import create_app, db, bcrypt
from project.models import User
from config import Config


# Cria uma configuração específica para testes que herda da oficial
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Força uso da RAM desde o início
    WTF_CSRF_ENABLED = False
    # Chave para testes (evita erro de sessão)
    SECRET_KEY = 'chave-secreta-apenas-para-testes-unitarios'


class BaseTestCase(unittest.TestCase):
    """Classe base para configuração de testes."""

    def setUp(self):
        # Passamos a TestConfig JÁ na criação do app.
        # Assim, o db.init_app() usa a memória RAM e nunca toca no expenses.db
        self.app = create_app(config_class=TestConfig)

        self.app_context = self.app.app_context()
        self.app_context.push()

        # Cria tabelas no banco em memória
        db.create_all()

        self.client = self.app.test_client()

        # Cria um usuário de teste padrão
        hashed_pw = bcrypt.generate_password_hash('senha123').decode('utf-8')
        self.test_user = User(name="Tester", email="test@example.com", password_hash=hashed_pw)
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        """Helper para logar o usuário de teste."""
        return self.client.post('/auth/login', data=dict(
            email="test@example.com",
            password="senha123"
        ), follow_redirects=True)