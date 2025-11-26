
# 📘 Documentação Técnica Completa  


# 1. Introdução

Este documento descreve a arquitetura completa do sistema, seus módulos, funcionalidades, fluxo de dados, recursos de IA e diagramas UML.

O sistema implementa:
- Análise financeira pessoal
- Previsão de gastos via ML
- Simulação de investimentos com volatilidade
- Painel com gráficos e KPIs
- Integração com notícias financeiras
- Blueprint architecture + Application Factory
- Banco de dados relacional
- API interna com módulos de IA

---

# 2. Arquitetura da Aplicação

A arquitetura combina MVC adaptado + micro-serviços internos de IA.

## 2.1. Component Diagram  

**Justificativa técnica:**  
Esse diagrama mostra **como o sistema é dividido em componentes** e como eles se comunicam:

- O **cliente** envia requisições para a aplicação Flask.
- A aplicação Flask é dividida em **Blueprints**, isolando responsabilidades:
  - `/auth`
  - `/`
  - `/investments`
- Os módulos de IA são tratados como serviços internos:
  - Previsão de gastos (`ai.py`)
  - Simulação de investimentos (`investing_ai.py`)
- O ORM centraliza persistência dos modelos User, Goal, Income e Expense.
- Serviços externos:
  - `yfinance` → preços de mercado
  - RSS → notícias
- Banco de dados e armazenamento fazem parte da camada de infra.

Essa separação permite **escalabilidade e teste modular**.

---

# 3. Deployment Diagram  

Mostra a **infraestrutura real**, incluindo:

- Usuário acessando via browser
- App Flask rodando em container
- Banco PostgreSQL ou SQLite
- Serviços externos (yfinance, RSS)
- Worker opcional para reprocessamento de IA
- Pipeline CI/CD
- Monitoramento

**Justificativa técnica:**  
Esse diagrama prova que seu sistema é **desplegável em nuvem**, e não apenas local.

Ele atende requisitos de:

- Cloud Computing  
- Modularidade  
- Alta disponibilidade  
- External Services Integration  

---

# 4. Sequence Diagrams  

## 4.1 Login / Registro / Logout  
Representam o fluxo de autenticação com base no `auth.routes`.  
Justificam:
- uso de Flask-Login  
- gestão de sessão  
- fluxo seguro  

## 4.2 Dashboard  
Mostram:
- Carregamento de metas  
- KPIs  
- Somatórios  
- IA de previsão  
- Preparação dos gráficos  

Baseado em `main.index`.

## 4.3 Controle Financeiro  
Usa `IncomeForm` e `ExpenseForm` e grava via SQLAlchemy.  

## 4.4 IA de Investimentos  
Baseado em `predict_investment()`:
- coleta yfinance  
- regressão linear  
- volatilidade  

## 4.5 Notícias  
`fetch_news()` com múltiplas fontes via RSS.

---

# 5. Class Diagram  

Mostra o modelo relacional:
- User  
- Goal  
- Income  
- Expense  

---

# 6. IA no Sistema

## 6.1 Previsão de Despesas
Baseado em regressão linear mensal.

Fluxo:
1. Extrai despesas  
2. Agrupa por mês  
3. Converte período para ordinal  
4. Treina modelo  
5. Calcula R² e MAE  
6. Prediz mês seguinte  

## 6.2 Simulador de Investimentos

Fluxo:
1. Coleta 2 anos de preços  
2. Converte datas em ordinais  
3. Treina regressão  
4. Calcula volatilidade → cone  
5. Retorna projeções  

---

# 7. Considerações e Conclusões

- Sistema completo para finanças pessoais  
- Integração IA/ML real funcional  
- Arquitetura profissional  
- Suporte a cloud e infraestrutura modular  
- Alto potencial de expansão  