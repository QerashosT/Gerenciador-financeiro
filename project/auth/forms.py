from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
from project.models import User
import re


class RegistrationForm(FlaskForm):
    """Formulário de Registro com validação forte de senha"""
    name = StringField('Nome',
                       validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('E-mail',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Senha',
                             validators=[
                                 DataRequired(),
                                 Length(min=8, message='A senha deve ter no mínimo 8 caracteres.'),
                             ])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[
                                         DataRequired(),
                                         EqualTo('password', message='As senhas devem ser iguais.')
                                     ])
    submit = SubmitField('Criar Conta')

    def validate_email(self, email):
        """Verifica se o e-mail já está em uso."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este e-mail já está em uso. Por favor, escolha outro.')

    def validate_password(self, password):
        """Valida a força da senha."""
        pwd = password.data

        # Verifica se tem pelo menos uma letra maiúscula
        if not re.search(r'[A-Z]', pwd):
            raise ValidationError('A senha deve conter pelo menos uma letra maiúscula.')

        # Verifica se tem pelo menos uma letra minúscula
        if not re.search(r'[a-z]', pwd):
            raise ValidationError('A senha deve conter pelo menos uma letra minúscula.')

        # Verifica se tem pelo menos um número
        if not re.search(r'\d', pwd):
            raise ValidationError('A senha deve conter pelo menos um número.')

        # Verifica se tem pelo menos um caractere especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
            raise ValidationError('A senha deve conter pelo menos um caractere especial (!@#$%^&*).')

        # Lista de senhas comuns proibidas
        common_passwords = [
            'password', '123456', '12345678', 'qwerty', 'abc123',
            'monkey', '1234567', 'letmein', 'trustno1', 'dragon',
            '123456789', 'senha123', 'senha', 'admin', 'admin123'
        ]

        if pwd.lower() in common_passwords:
            raise ValidationError('Esta senha é muito comum. Por favor, escolha uma senha mais forte.')


class LoginForm(FlaskForm):
    """Formulário de Login"""
    email = StringField('E-mail',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Senha',
                             validators=[DataRequired()])
    remember = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')