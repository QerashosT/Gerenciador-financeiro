from flask import render_template, redirect, url_for, flash, request, session
from flask.blueprints import Blueprint
from project import db, bcrypt
from project.models import User
from project.auth.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__, template_folder='../templates')

# Dicionário para rastrear tentativas de login (em produção, use Redis ou banco de dados)
login_attempts = {}


def check_login_attempts(email):
    """Verifica se o usuário excedeu o limite de tentativas de login."""
    now = datetime.now()

    if email in login_attempts:
        attempts, last_attempt = login_attempts[email]

        # Se passou mais de 15 minutos, resetar tentativas
        if now - last_attempt > timedelta(minutes=15):
            login_attempts[email] = (0, now)
            return True

        # Se excedeu 5 tentativas
        if attempts >= 5:
            time_left = 15 - int((now - last_attempt).seconds / 60)
            flash(f'Muitas tentativas de login. Tente novamente em {time_left} minutos.', 'danger')
            return False
    else:
        login_attempts[email] = (0, now)

    return True


def record_login_attempt(email, success=False):
    """Registra uma tentativa de login."""
    now = datetime.now()

    if success:
        # Limpar tentativas em caso de sucesso
        if email in login_attempts:
            del login_attempts[email]
    else:
        # Incrementar tentativas falhadas
        if email in login_attempts:
            attempts, _ = login_attempts[email]
            login_attempts[email] = (attempts + 1, now)
        else:
            login_attempts[email] = (1, now)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Cria o hash da senha
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password_hash=hashed_password)

        # Adiciona o usuário ao DB
        db.session.add(user)
        db.session.commit()

        flash('Sua conta foi criada! Você já pode fazer o login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', title='Registrar', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data

        # Verificar tentativas de login
        if not check_login_attempts(email):
            return render_template('login.html', title='Login', form=form)

        user = User.query.filter_by(email=email).first()

        # Verifica se o usuário existe e se a senha está correta
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            record_login_attempt(email, success=True)

            # Redireciona para a página que o usuário tentou acessar (ou para o index)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            record_login_attempt(email, success=False)
            flash('Login sem sucesso. Por favor, verifique o e-mail e a senha.', 'danger')

    return render_template('login.html', title='Login', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))