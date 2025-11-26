# 💰 Gerenciador Financeiro Inteligente  
### *Sistema com Machine Learning para previsão financeira, análise de investimentos e acompanhamento de metas*

Este projeto é um gerenciador financeiro completo desenvolvido em **Python + Flask**, com módulos dedicados a:

- Controle financeiro (receitas e despesas)
- Metas financeiras
- Dashboard inteligente com KPIs
- Previsão de despesas com **Machine Learning**
- Simulador de investimentos usando **IA + volatilidade**
- Notícias financeiras via RSS
- Arquitetura escalável (Blueprints + Application Factory)
- Banco em PostgreSQL ou SQLite
- Diagramas UML completos (Arquitetura, Componentes, Sequências, Classes e Deployment)

---

# 📌 Tecnologias Utilizadas

### **Backend**
- Python 3.10+
- Flask (Blueprints + App Factory)
- SQLAlchemy ORM
- Flask-Login
- bcrypt

### **Machine Learning**
- scikit-learn  
- Pandas  
- NumPy  
- yfinance (investimentos)

### **Frontend**
- Jinja2 Templates  
- Chart.js  
- IMask.js  
- AJAX / Fetch API  

### **Infra**
- PostgreSQL
- Docker (opcional)
- Cloud Storage (S3) — opcional
- yfinance (dados de mercado)
- RSS Feedparser

---

# 🌐 Arquitetura Geral

A aplicação segue a abordagem **MVC adaptado**, usando:

- **Blueprints**
  - `auth` → autenticação  
  - `main` → dashboard, metas, controle financeiro  
  - `investments` → IA de investimentos

- **Application Factory (`create_app`)**

- **Camadas**
  - Roteamento/Controller  
  - Serviço de IA  
  - Modelos ORM  
  - Templates/Jinja  
  - Banco de Dados  

---

# 🧠 Machine Learning

A aplicação possui **dois modelos distintos**:

### ✔️ Previsão de Despesas — Regressão Linear  
Arquivo: `project/utils/ai.py`  
- Treina dinamicamente com gastos mensais do usuário  
- Calcula R², MAE  
- Retorna tendência (crescente/decrescente)

### ✔️ Simulador de Investimentos — Linear Regression + Volatilidade  
Arquivo: `project/utils/investing_ai.py`  
- Obtém histórico de preços via yfinance  
- Calcula preço futuro com incerteza (otimista, realista, pessimista)  
- Converte tudo para retorno financeiro (quantidade x preço projetado)

---

# 🗂 Estrutura do Projeto
```
project/
│
├── auth/
│ └── routes.py
├── main/
│ └── routes.py
├── investments/
│ └── routes.py
│
├── utils/
│ ├── ai.py
│ ├── investing_ai.py
│ └── news.py
│
├── models.py
├── static/
└── templates/
```
---

# 📊 DASHBOARD (KPIs)

- Receita total (mês)
- Despesa total (mês)
- Economia do mês
- Progresso da meta principal
- Gráficos por categoria
- Gráficos de tendência 6 meses
- Previsão de gastos da IA
- Últimas transações

---

# 📐 Diagramas UML

Todos os diagramas estão disponíveis em:  
`docs/uml/`

### **Inclui:**
- Component Diagram  
- Deployment Diagram  
- Sequence Diagrams:
  - Login  
  - Dashboard  
  - Controle Financeiro  
  - IA de Investimentos  
  - Notícias  
- Class Diagram

---

# 🚀 Como executar

```bash
pip install -r requirements.txt
flask run
```
Para usar PostgreSQL:
```
export DATABASE_URL="postgresql://user:pass@host/db"
```

---


