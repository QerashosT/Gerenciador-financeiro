from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from project.utils.investing_ai import predict_investment

investments = Blueprint('investments', __name__, template_folder='../templates')


@investments.route('/investments')
@login_required
def index():
    return render_template('investments.html', title="Simulador de Investimentos")


@investments.route('/api/simulate', methods=['POST'])
@login_required
def simulate():
    data = request.get_json()
    ticker = data.get('ticker')
    amount = float(data.get('amount', 0))
    months = int(data.get('months', 12))

    if not ticker or amount <= 0:
        return jsonify({"error": "Dados inválidos"}), 400

    result = predict_investment(ticker, amount, months)
    return jsonify(result)