from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from project.models import User

class RegistrationForm(FlaskForm):
    """Formulário de Registro"""
    name = StringField('Nome',
                       validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('E-mail',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Senha',
                             validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')])
    submit = SubmitField('Criar Conta')

    def validate_email(self, email):
        """Verifica se o e-mail já está em uso."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este e-mail já está em uso. Por favor, escolha outro.')

class LoginForm(FlaskForm):
    """Formulário de Login"""
    email = StringField('E-mail',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Senha',
                             validators=[DataRequired()])
    remember = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')
