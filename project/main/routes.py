from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from project.models import Goal, Income, Expense
from project import db
from project.main.forms import IncomeForm, ExpenseForm, GoalForm
from datetime import datetime
from dateutil.relativedelta import relativedelta  # Importe para lidar com meses

# ... (seu main, EXPENSE_CATEGORIES, e CATEGORY_ICONS) ...
main = Blueprint('main', __name__, template_folder='../templates')
EXPENSE_CATEGORIES = [
    'Alimentação',
    'Transporte',
    'Moradia',
    'Saúde',
    'Lazer',
    'Educação',
    'Roupas',
    'Serviços',
    'Outra'
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
    today = datetime.utcnow()

    # 1. KPIs do Mês Atual (Receita, Despesa, Saldo)
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
    current_savings = 0
    if main_goal:
        total_savings_all_time = db.session.query(db.func.sum(Income.amount)).filter(
            Income.user_id == current_user.id).scalar() or 0.0
        total_expenses_all_time = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id).scalar() or 0.0
        current_savings = total_savings_all_time - total_expenses_all_time

        main_goal.current_amount = current_savings  # Atualiza valor para exibição

        if main_goal.target_amount > 0 and current_savings > 0:
            goal_progress = (current_savings / main_goal.target_amount) * 100
        goal_progress = max(0, min(100, goal_progress))

    # 3. Gráfico de Categoria (Doughnut)
    category_data = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount)
    ).filter(
        Expense.user_id == current_user.id,
        db.extract('month', Expense.date) == today.month,
        db.extract('year', Expense.date) == today.year
    ).group_by(Expense.category).order_by(db.func.sum(Expense.amount).desc()).all()

    # 4. Gráfico de Tendência (Line) - Últimos 6 meses
    trend_labels = []
    trend_incomes = []
    trend_expenses = []

    for i in range(5, -1, -1):  # De 5 meses atrás (5) até o mês atual (0)
        month_date = today - relativedelta(months=i)
        trend_labels.append(month_date.strftime("%b %Y"))

        # Total de Receitas no mês
        month_income = db.session.query(db.func.sum(Income.amount)).filter(
            Income.user_id == current_user.id,
            db.extract('month', Income.date) == month_date.month,
            db.extract('year', Income.date) == month_date.year
        ).scalar() or 0.0
        trend_incomes.append(month_income)

        # Total de Despesas no mês
        month_expense = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            db.extract('month', Expense.date) == month_date.month,
            db.extract('year', Expense.date) == month_date.year
        ).scalar() or 0.0
        trend_expenses.append(month_expense)

    trend_data = {
        "labels": trend_labels,
        "incomes": trend_incomes,
        "expenses": trend_expenses
    }

    # 5. Transações Recentes
    recent_incomes = Income.query.filter_by(owner=current_user).order_by(Income.date.desc()).limit(5).all()
    recent_expenses = Expense.query.filter_by(owner=current_user).order_by(Expense.date.desc()).limit(5).all()

    # Combina e formata as transações
    all_transactions = []
    for item in recent_incomes:
        all_transactions.append({"type": "income", "item": item})
    for item in recent_expenses:
        all_transactions.append({"type": "expense", "item": item})

    # Ordena pela data e pega os 5 mais recentes
    recent_transactions = sorted(all_transactions, key=lambda x: x['item'].date, reverse=True)[:5]

    return render_template('index.html',
                           title='Dashboard',
                           main_goal=main_goal,
                           goal_progress=goal_progress,
                           total_income=total_income,
                           total_expense=total_expense,
                           savings=savings,
                           goal_form=goal_form,
                           category_icons=CATEGORY_ICONS,  # Para o card "Maiores Gastos"
                           category_data=category_data,  # Para o Gráfico e o Card "Maiores Gastos"
                           trend_data=trend_data,  # Para o Gráfico de Linha
                           recent_transactions=recent_transactions  # Para a lista
                           )


@main.route('/controle', methods=['GET', 'POST'])
@login_required
def controle():
    # ... (Sua rota de controle - sem mudanças) ...
    income_form = IncomeForm(prefix='income')
    expense_form = ExpenseForm(prefix='expense')
    expense_form.category.choices = [(c, c) for c in EXPENSE_CATEGORIES]
    if request.method == "GET":
        if not income_form.date.data:
            income_form.date.data = datetime.utcnow().date()
        if not expense_form.date.data:
            expense_form.date.data = datetime.utcnow().date()
    if 'income-submit_income' in request.form and income_form.validate_on_submit():
        new_income = Income(description=income_form.description.data,
                            amount=income_form.amount.data,
                            date=income_form.date.data,
                            owner=current_user)
        db.session.add(new_income)
        db.session.commit()
        flash('Receita adicionada com sucesso!', 'success')
        return redirect(url_for('main.controle'))
    if 'expense-submit_expense' in request.form and expense_form.validate_on_submit():
        new_expense = Expense(description=expense_form.description.data,
                              amount=expense_form.amount.data,
                              category=expense_form.category.data,
                              date=expense_form.date.data,
                              owner=current_user)
        db.session.add(new_expense)
        db.session.commit()
        flash('Despesa adicionada com sucesso!', 'success')
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
    # ... (sem mudanças) ...
    item = Income.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('Receita excluída.', 'success')
    return redirect(url_for('main.controle'))


@main.route('/delete/expense/<int:item_id>', methods=['POST'])
@login_required
def delete_expense(item_id):
    # ... (sem mudanças) ...
    item = Expense.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('Despesa excluída.', 'success')
    return redirect(url_for('main.controle'))