from flask import render_template, redirect, url_for, flash, request
from flask.blueprints import Blueprint
from project import db, bcrypt
from project.models import User
from project.auth.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required

# Cria o Blueprint
auth = Blueprint('auth', __name__, template_folder='../templates')


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
        user = User.query.filter_by(email=form.email.data).first()

        # Verifica se o usuário existe e se a senha está correta
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            # Redireciona para a página que o usuário tentou acessar (ou para o index)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login sem sucesso. Por favor, verifique o e-mail e a senha.', 'danger')

    return render_template('login.html', title='Login', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))