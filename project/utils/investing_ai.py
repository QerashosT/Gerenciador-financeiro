import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import warnings

# Ignora warnings específicos do sklearn sobre feature names
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")


def predict_investment(ticker, amount, months):
    """
    Analisa um ativo financeiro e projeta retorno futuro usando ML.
    """
    try:
        # 1. Coleta de Dados
        symbol = ticker.upper().strip()

        # Lógica de sufixo inteligente
        if not symbol.endswith('.SA') and not symbol.endswith('-USD'):
            # Se tem 5 ou 6 letras e termina com número (ex: PETR4, VALE3), é Brasil
            if len(symbol) >= 5 and symbol[-1].isdigit():
                symbol += '.SA'
            # Se não, assume que é EUA ou Cripto e tenta como está

        stock = yf.Ticker(symbol)

        # Tenta pegar histórico. Se falhar, yfinance geralmente retorna vazio ou erro.
        try:
            hist = stock.history(period="2y")
        except Exception:
            return {"error": f"Ativo '{symbol}' não encontrado na bolsa."}

        if hist.empty or len(hist) < 30:
            return {"error": f"Dados insuficientes ou ativo '{symbol}' não encontrado."}

        # 2. Preparação dos Dados
        hist = hist.reset_index()
        hist['DateOrdinal'] = hist['Date'].map(datetime.toordinal)

        # Converte para array numpy para evitar o warning de feature names
        X = hist[['DateOrdinal']].to_numpy()
        y = hist['Close'].to_numpy()

        # 3. Treinamento
        model = LinearRegression()
        model.fit(X, y)

        # 4. Volatilidade (Risco)
        hist['Returns'] = hist['Close'].pct_change()
        daily_volatility = hist['Returns'].std()
        # Se volatilidade for NaN (dados ruins), assume um padrão alto
        if pd.isna(daily_volatility): daily_volatility = 0.02

        monthly_volatility = daily_volatility * np.sqrt(21)

        # 5. Projeção
        future_dates = []
        projected_prices = []
        optimistic_prices = []
        pessimistic_prices = []

        last_date = hist['Date'].iloc[-1]
        current_price = hist['Close'].iloc[-1]
        shares_bought = amount / current_price

        for i in range(1, months + 1):
            future_date = last_date + timedelta(days=i * 30)
            # Input também como numpy array
            future_ordinal = np.array([[future_date.toordinal()]])

            trend_price = model.predict(future_ordinal)[0]

            # Cone de incerteza
            uncertainty = monthly_volatility * np.sqrt(i) * trend_price

            future_dates.append(future_date.strftime('%m/%Y'))

            opt_price = trend_price + uncertainty
            pes_price = trend_price - uncertainty

            projected_prices.append(round(trend_price * shares_bought, 2))
            optimistic_prices.append(round(opt_price * shares_bought, 2))
            pessimistic_prices.append(round(pes_price * shares_bought, 2))

        return {
            "status": "success",
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "shares": round(shares_bought, 4),
            "labels": future_dates,
            "projected": projected_prices,
            "optimistic": optimistic_prices,
            "pessimistic": pessimistic_prices
        }

    except Exception as e:
        print(f"Erro na IA: {e}")
        return {"error": "Erro interno ao analisar o ativo. Tente novamente."}