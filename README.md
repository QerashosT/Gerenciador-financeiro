<img height="200" alt="image" src="https://github.com/user-attachments/assets/ee8c0ce4-14c5-45d6-ad5f-835937d63b52" />

# Me Ajuda AI 🧠💰

> **Seu dinheiro, seus sonhos.**  
> Uma plataforma de gestão financeira inteligente impulsionada por Inteligência Artificial.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

---

## 📋 Sobre o Projeto

O **Me Ajuda AI** não é apenas mais uma planilha digital. É uma solução desenvolvida para resolver o problema da **imprevisibilidade financeira** enfrentada por indivíduos e pequenas empresas.

Diferente de apps tradicionais que apenas registram o passado, nosso sistema utiliza algoritmos de **Machine Learning** para projetar o futuro, ajudando o usuário a tomar decisões hoje para alcançar metas de longo prazo.

---

## ✨ Funcionalidades Principais

### 1. 📊 Dashboard Inteligente
* **KPIs em Tempo Real:** Monitoramento de Receitas, Despesas e Saldo com indicadores de tendência comparativa (vs. mês anterior).
* **Visualização de Dados:** Gráficos dinâmicos (Pizza e Linha) utilizando **Chart.js**.
* **Listas Dinâmicas:** Top despesas por categoria e transações recentes.

### 2. 🤖 Inteligência Artificial Aplicada
O sistema possui dois motores de IA distintos:
* **Previsão de Gastos (Budget Forecasting):** Utiliza **Regressão Linear (Scikit-Learn)** para analisar o histórico de consumo e prever o fechamento da fatura do próximo mês. Inclui métricas de precisão (R² e MAE) para total transparência.
* **Simulador de Investimentos (Asset Prediction):** Integração com dados reais da bolsa (**Yfinance**). Projeta rentabilidade futura criando um "Cone de Volatilidade" com cenários Otimista, Realista (IA) e Pessimista.

### 3. 🎯 Gestão de Metas
* Foco na realização de sonhos.
* Modal interativo para criação e edição de objetivos financeiros.
* Barra de progresso visual baseada no saldo acumulado.

### 4. 📰 Notícias do Mercado
* Agregador de notícias em tempo real (RSS).
* Filtros por temas (Cripto, Agro, Economia) e busca inteligente.
* Carregamento assíncrono (SPA Híbrida) para não travar a navegação.

---

## 🛠️ Arquitetura e Tecnologias

O projeto segue o padrão **MVC (Model-View-Controller)** com arquitetura modular baseada em **Blueprints**.

### Backend
* **Linguagem:** Python 3
* **Framework:** Flask
* **Banco de Dados:** SQLAlchemy ORM (SQLite em Dev / PostgreSQL em Prod)
* **Data Science:** Pandas, NumPy, Scikit-Learn, Yfinance
* **Autenticação:** Flask-Login & Bcrypt

### Frontend
* **Template Engine:** Jinja2 (Server-side rendering)
* **Estilização:** CSS3 Modular (Design System próprio)
* **Interatividade:** JavaScript Vanilla, Chart.js (Gráficos), IMask (Máscaras de Input)

### Infraestrutura
* **Containerização:** Docker
* **Configuração:** Variáveis de ambiente (.env)
* **Cloud Agnostic:** Pronto para deploy em Google Cloud Run, AWS ou Render.

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
* Python 3.10 ou superior
* Git

### Passo a Passo

1.  **Clone o repositório**
    ```bash
    git clone [https://github.com/seu-usuario/Gerenciador-financeiro.git](https://github.com/seu-usuario/Gerenciador-financeiro.git)
    cd Gerenciador-financeiro
    ```

2.  **Crie e ative um ambiente virtual**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as Variáveis de Ambiente**
    Crie um arquivo `.env` na raiz do projeto e adicione uma chave secreta:
    ```env
    SECRET_KEY=sua-chave-secreta-aqui
    # Opcional: URL do banco de dados (se não informado, usa SQLite local)
    # DATABASE_URL=postgresql://user:pass@localhost/dbname
    ```

5.  **Inicie o Banco de Dados e Rode a Aplicação**
    ```bash
    python run.py
    ```
    *O sistema criará automaticamente o arquivo `expenses.db` na primeira execução.*

6.  **Acesse no Navegador**
    Abra `http://127.0.0.1:4025`

---

## ✅ Testes

O projeto possui uma suíte de testes unitários e funcionais para garantir a integridade dos cálculos financeiros e da IA.

Para rodar os testes:
```bash
python -m unittest discover tests
