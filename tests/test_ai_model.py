import unittest
from datetime import datetime, timedelta
from tests.base import BaseTestCase
from project import db
from project.models import Expense
from project.utils.ai import predict_next_month_expenses


class TestAIModel(BaseTestCase):

    def create_historical_data(self):
        """Helper para criar um cenário de gastos crescentes."""
        # Mês 1: R$ 1000
        date1 = datetime.now() - timedelta(days=90)
        e1 = Expense(description="Mês 1", amount=1000.0, category="Geral", date=date1, user_id=self.test_user.id)

        # Mês 2: R$ 2000
        date2 = datetime.now() - timedelta(days=60)
        e2 = Expense(description="Mês 2", amount=2000.0, category="Geral", date=date2, user_id=self.test_user.id)

        # Mês 3: R$ 3000
        date3 = datetime.now() - timedelta(days=30)
        e3 = Expense(description="Mês 3", amount=3000.0, category="Geral", date=date3, user_id=self.test_user.id)

        db.session.add_all([e1, e2, e3])
        db.session.commit()

    def test_ai_insufficient_data(self):
        """Cenário 1: Valida comportamento com poucos dados."""
        # Apenas 1 despesa
        e1 = Expense(description="Única", amount=100.0, category="Geral", date=datetime.now(),
                     user_id=self.test_user.id)
        db.session.add(e1)
        db.session.commit()

        result = predict_next_month_expenses(self.test_user.id)

        # Deve retornar status de dados insuficientes
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'insufficient_data')

    def test_ai_linear_growth(self):
        """Cenário 2: Valida predição em tendência linear perfeita."""
        self.create_historical_data()

        # Se gastou 1000, 2000, 3000... a IA deve prever 4000 para o próximo mês
        result = predict_next_month_expenses(self.test_user.id)

        self.assertEqual(result['status'], 'success')
        # Tolerância pequena para erros de ponto flutuante
        self.assertAlmostEqual(result['predicted_value'], 4000.0, delta=10.0)
        self.assertEqual(result['trend'], 'Crescente')

        # Em uma reta perfeita, o R2 deve ser 1.0
        self.assertAlmostEqual(result['r2_score'], 1.0, delta=0.01)

    def test_ai_metrics_calculation(self):
        """Cenário 3: Valida se as métricas (MAE, R2) estão sendo retornadas."""
        self.create_historical_data()
        result = predict_next_month_expenses(self.test_user.id)

        self.assertIn('mae', result)
        self.assertIn('r2_score', result)
        self.assertIsInstance(result['mae'], float)


if __name__ == "__main__":
    unittest.main()