import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from project import db
from project.models import Expense


def predict_next_month_expenses(user_id):
    """
    Utiliza Regressão Linear para prever os gastos do próximo mês.
    Retorna um dicionário com a previsão e métricas de qualidade.
    """
    # 1. Extração de Dados (SQLAlchemy -> Pandas)
    query = db.session.query(Expense).filter_by(user_id=user_id)

    # Usamos db.session.connection() para garantir compatibilidade com Pandas
    try:
        df = pd.read_sql(query.statement, db.session.connection())
    except Exception:
        # Fallback para versões antigas ou SQLite simples
        df = pd.read_sql(query.statement, db.session.bind)
    # ---------------------

    # Validação: Precisamos de dados
    if df.empty:
        return None

    # 2. Pré-processamento e Estrutura de Dados (Pandas)
    df['date'] = pd.to_datetime(df['date'])

    # Agrupamos por mês e somamos o valor
    monthly_data = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().reset_index()

    if len(monthly_data) < 2:
        return {
            "status": "insufficient_data",
            "message": "Precisamos de dados de pelo menos 2 meses para gerar previsões."
        }

    # Transformamos o período em número ordinal para o eixo X
    monthly_data['month_index'] = range(len(monthly_data))

    X = monthly_data[['month_index']]
    y = monthly_data['amount']

    # 3. Treinamento do Modelo
    model = LinearRegression()
    model.fit(X, y)

    # 4. Predição (Próximo mês)
    next_month_index = [[len(monthly_data)]]
    prediction = model.predict(next_month_index)[0]

    prediction = max(0, round(prediction, 2))

    # 5. Métricas de Avaliação
    y_pred_hist = model.predict(X)
    r2 = r2_score(y, y_pred_hist)
    mae = mean_absolute_error(y, y_pred_hist)

    return {
        "status": "success",
        "predicted_value": prediction,
        "r2_score": round(r2, 2),
        "mae": round(mae, 2),
        "trend": "Crescente" if model.coef_[0] > 0 else "Decrescente"
    }