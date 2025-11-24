from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from project.models import Goal, Income, Expense
from project import db
from project.main.forms import IncomeForm, ExpenseForm, GoalForm
from project.utils.ai import predict_next_month_expenses
from project.utils.news import fetch_news
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import json

main = Blueprint('main', __name__, template_folder='../templates')

EXPENSE_CATEGORIES = [
    'Alimentação', 'Transporte', 'Moradia', 'Saúde', 'Lazer',
    'Educação', 'Roupas', 'Serviços', 'Outra'
]
CATEGORY_ICONS = {
    'Alimentação': 'fa-solid fa-utensils',
    'Transporte': 'fa-solid fa-car-side',
    'Moradia': 'fa-solid fa-house-chimney',
    'Saúde': 'fa-solid fa-briefcase-medical',
    'Lazer': 'fa-solid fa-film',
    'Educação': 'fa-solid fa-book-open',
    'Roupas': 'fa-solid fa-shirt',
    'Serviços': 'fa-solid fa-receipt',
    'Outra': 'fa-solid fa-circle-question',
    'default': 'fa-solid fa-dollar-sign'
}


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    goal_form = GoalForm(prefix='goal')
    user_goals = Goal.query.filter_by(owner=current_user).order_by(Goal.created_at.desc()).all()
    main_goal = user_goals[0] if user_goals else None

    if 'goal-submit_goal' in request.form and goal_form.validate_on_submit():
        if main_goal:
            main_goal.name = goal_form.name.data
            main_goal.target_amount = goal_form.target_amount.data
            main_goal.target_date = goal_form.target_date.data
        else:
            new_goal = Goal(
                name=goal_form.name.data,
                target_amount=goal_form.target_amount.data,
                target_date=goal_form.target_date.data,
                current_amount=0,
                owner=current_user
            )
            db.session.add(new_goal)
        db.session.commit()
        flash('Meta salva com sucesso!', 'success')
        return redirect(url_for('main.index'))

    if request.method == "GET" and main_goal:
        goal_form.name.data = main_goal.name
        goal_form.target_amount.data = main_goal.target_amount
        goal_form.target_date.data = main_goal.target_date

    # --- LÓGICA DO DASHBOARD ---
    today = datetime.now(timezone.utc)

    # 1. KPIs
    incomes_mes = Income.query.filter(
        db.extract('month', Income.date) == today.month,
        db.extract('year', Income.date) == today.year,
        Income.user_id == current_user.id
    ).all()
    expenses_mes = Expense.query.filter(
        db.extract('month', Expense.date) == today.month,
        db.extract('year', Expense.date) == today.year,
        Expense.user_id == current_user.id
    ).all()
    total_income = sum(i.amount for i in incomes_mes)
    total_expense = sum(e.amount for e in expenses_mes)
    savings = total_income - total_expense

    # 2. Progresso da Meta
    goal_progress = 0
    if main_goal:
        total_savings = db.session.query(db.func.sum(Income.amount)).filter(
            Income.user_id == current_user.id).scalar() or 0.0
        total_expenses = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id).scalar() or 0.0
        current_val = total_savings - total_expenses
        main_goal.current_amount = current_val
        if main_goal.target_amount > 0 and current_val > 0:
            goal_progress = (current_val / main_goal.target_amount) * 100
        goal_progress = max(0, min(100, goal_progress))

    # 3. GRÁFICO DE CATEGORIA
    # Usamos float() para garantir que não vá Decimal para o JSON
    cat_query = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount)
    ).filter(
        Expense.user_id == current_user.id,
        db.extract('month', Expense.date) == today.month,
        db.extract('year', Expense.date) == today.year
    ).group_by(Expense.category).all()

    # Formato: [['Alimentação', 150.00], ['Lazer', 50.00]]
    category_data = [[c[0], float(c[1])] for c in cat_query] if cat_query else []

    # 4. GRÁFICO DE TENDÊNCIA
    trend_labels = []
    trend_incomes = []
    trend_expenses = []

    for i in range(5, -1, -1):
        month_date = today - relativedelta(months=i)
        trend_labels.append(month_date.strftime("%b"))  # Ex: "Nov"

        # Coalesce (ou 0.0) para evitar None
        inc = db.session.query(db.func.sum(Income.amount)).filter(
            Income.user_id == current_user.id,
            db.extract('month', Income.date) == month_date.month,
            db.extract('year', Income.date) == month_date.year
        ).scalar() or 0.0

        exp = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            db.extract('month', Expense.date) == month_date.month,
            db.extract('year', Expense.date) == month_date.year
        ).scalar() or 0.0

        trend_incomes.append(float(inc))
        trend_expenses.append(float(exp))

    trend_data = {
        "labels": trend_labels,
        "incomes": trend_incomes,
        "expenses": trend_expenses
    }

    # 5. INTELIGÊNCIA ARTIFICIAL
    ai_prediction = predict_next_month_expenses(current_user.id)

    # 6. Transações Recentes
    recent_incomes = Income.query.filter_by(owner=current_user).order_by(Income.date.desc()).limit(5).all()
    recent_expenses = Expense.query.filter_by(owner=current_user).order_by(Expense.date.desc()).limit(5).all()
    all_transactions = []
    for item in recent_incomes: all_transactions.append({"type": "income", "item": item})
    for item in recent_expenses: all_transactions.append({"type": "expense", "item": item})
    recent_transactions = sorted(all_transactions, key=lambda x: x['item'].date, reverse=True)[:5]

    return render_template('index.html',
                           title='Dashboard',
                           main_goal=main_goal,
                           goal_progress=goal_progress,
                           total_income=total_income,
                           total_expense=total_expense,
                           savings=savings,
                           goal_form=goal_form,
                           category_icons=CATEGORY_ICONS,
                           category_data=category_data,
                           trend_data=trend_data,
                           ai_prediction=ai_prediction,  # <--- Passando IA
                           recent_transactions=recent_transactions)


@main.route('/controle', methods=['GET', 'POST'])
@login_required
def controle():
    income_form = IncomeForm(prefix='income')
    expense_form = ExpenseForm(prefix='expense')
    expense_form.category.choices = [(c, c) for c in EXPENSE_CATEGORIES]

    if request.method == "GET":
        if not income_form.date.data: income_form.date.data = datetime.now(timezone.utc).date()
        if not expense_form.date.data: expense_form.date.data = datetime.now(timezone.utc).date()

    if 'income-submit_income' in request.form and income_form.validate_on_submit():
        # ... lógica de salvar ...
        new_income = Income(description=income_form.description.data, amount=income_form.amount.data,
                            date=income_form.date.data, owner=current_user)
        db.session.add(new_income)
        db.session.commit()
        return redirect(url_for('main.controle'))

    if 'expense-submit_expense' in request.form and expense_form.validate_on_submit():
        # ... lógica de salvar ...
        new_expense = Expense(description=expense_form.description.data, amount=expense_form.amount.data,
                              category=expense_form.category.data, date=expense_form.date.data, owner=current_user)
        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for('main.controle'))

    incomes = Income.query.filter_by(owner=current_user).order_by(Income.date.desc()).limit(10).all()
    expenses = Expense.query.filter_by(owner=current_user).order_by(Expense.date.desc()).limit(10).all()

    return render_template('controle.html',
                           title='Controle Financeiro',
                           income_form=income_form,
                           expense_form=expense_form,
                           incomes=incomes,
                           expenses=expenses,
                           category_icons=CATEGORY_ICONS)


@main.route('/delete/income/<int:item_id>', methods=['POST'])
@login_required
def delete_income(item_id):
    item = Income.query.get_or_404(item_id)
    if item.owner != current_user: abort(403)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('main.controle'))


@main.route('/delete/expense/<int:item_id>', methods=['POST'])
@login_required
def delete_expense(item_id):
    item = Expense.query.get_or_404(item_id)
    if item.owner != current_user: abort(403)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('main.controle'))

@main.route("/news")
@login_required
def news_page():
    """
    Nova Rota: Renderiza APENAS o container com o loader.
    O conteúdo será carregado via AJAX pelo cliente.
    """
    return render_template("news.html", title="Notícias") # Não passamos mais 'news'

@main.route("/api/news")
@login_required
def api_news():
    """API endpoint que faz o trabalho pesado de buscar notícias."""
    limit = int(request.args.get("limit", 12))
    items = fetch_news(limit=limit)
    return jsonify(items)