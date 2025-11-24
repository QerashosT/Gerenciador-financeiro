import unittest
from tests.base import BaseTestCase
from project.models import User, Expense, Income


class TestRoutes(BaseTestCase):

    def test_index_redirect(self):
        """Teste: Acesso à home sem login deve redirecionar."""
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_login_successful(self):
        """Teste: Login com credenciais corretas."""
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

    def test_add_expense(self):
        """Teste Funcional: Adicionar uma despesa via rota."""
        self.login()

        # Simula o envio do formulário de despesa (note os prefixos 'expense-')
        response = self.client.post('/controle', data={
            'expense-description': 'Teste Unitário',
            'expense-amount': '150.00',
            'expense-category': 'Alimentação',
            'expense-date': '2023-12-01',
            'expense-submit_expense': 'Adicionar Despesa'  # Botão de submit
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Verifica se salvou no banco
        expense = Expense.query.filter_by(description='Teste Unitário').first()
        self.assertIsNotNone(expense)
        self.assertEqual(expense.amount, 150.00)

    def test_add_income(self):
        """Teste Funcional: Adicionar uma receita."""
        self.login()

        response = self.client.post('/controle', data={
            'income-description': 'Salário Teste',
            'income-amount': '5000.00',
            'income-date': '2023-12-01',
            'income-submit_income': 'Adicionar Receita'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        income = Income.query.filter_by(description='Salário Teste').first()
        self.assertIsNotNone(income)
        self.assertEqual(income.amount, 5000.00)


if __name__ == "__main__":
    unittest.main()