from project import db, login_manager
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    """Callback usado pelo Flask-Login para carregar um usuário pelo ID."""
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """Modelo de Usuário para autenticação."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relacionamentos
    goals = db.relationship('Goal', backref='owner', lazy=True, cascade="all, delete-orphan")
    incomes = db.relationship('Income', backref='owner', lazy=True, cascade="all, delete-orphan")
    expenses = db.relationship('Expense', backref='owner', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"


class Goal(db.Model):
    """Modelo para as Metas (o foco principal)."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, nullable=False, default=0.0)
    target_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Chave estrangeira para o Usuário
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Goal('{self.name}', Target: {self.target_amount})"


class Income(db.Model):
    """Modelo para Rendas."""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow, index=True)

    # Chave estrangeira para o Usuário
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Income('{self.description}', Amount: {self.amount})"


class Expense(db.Model):
    """Seu modelo de Despesa, agora ligado a um usuário."""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(128), default='Geral', index=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow, index=True)  # Mudei para Date object

    # Chave estrangeira para o Usuário
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        """Função utilitária (você já tinha)"""
        return dict(id=self.id,
                    description=self.description,
                    amount=self.amount,
                    category=self.category,
                    date=self.date.isoformat())

    def __repr__(self):
        return f"Expense('{self.description}', Amount: {self.amount})"