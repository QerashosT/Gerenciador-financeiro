from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, SelectField  # 1. IMPORTE O SelectField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, NumberRange


class IncomeForm(FlaskForm):
    description = StringField('Descrição', validators=[DataRequired()])
    amount = FloatField('Valor', validators=[DataRequired(), NumberRange(min=0.01)])
    date = DateField('Data', validators=[DataRequired()], format='%Y-%m-%d')
    submit_income = SubmitField('Adicionar Receita')


class ExpenseForm(FlaskForm):
    """Formulário para adicionar/editar Despesa"""
    description = StringField('Descrição', validators=[DataRequired()])
    amount = FloatField('Valor', validators=[DataRequired(), NumberRange(min=0.01)])
    category = SelectField('Categoria', validators=[DataRequired()])
    date = DateField('Data', validators=[DataRequired()], format='%Y-%m-%d')
    submit_expense = SubmitField('Adicionar Despesa')

class GoalForm(FlaskForm):
    """Formulário para criar/editar Meta"""
    name = StringField('Nome da Meta', validators=[DataRequired()])
    target_amount = FloatField('Valor Alvo', validators=[DataRequired(), NumberRange(min=0.01)])
    target_date = DateField('Data Alvo (Opcional)', validators=[], format='%Y-%m-%d')
    submit_goal = SubmitField('Salvar Meta')