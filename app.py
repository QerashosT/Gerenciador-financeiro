from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import feedparser
import os, io, csv, json, re
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from rust_structures import Counter

BASE_DIR = os.path.dirname(__file__)

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"), static_folder=os.path.join(BASE_DIR, "static"))
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'expenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(128), default='Geral')
    date = db.Column(db.String(20), nullable=False)  # ISO 'YYYY-MM-DD'

    def to_dict(self):
        return dict(id=self.id, description=self.description, amount=self.amount, category=self.category, date=self.date)

with app.app_context():
    db.create_all()

# --- RSS feeds (Portuguese / Brazil-focused)
RSS_SOURCES = {
    "G1 (Economia)": "https://g1.globo.com/economia/rss/",
    "Valor Econômico": "https://valor.globo.com/rss.xml",
    "Exame": "https://exame.com/feed/",
    "InfoMoney": "https://www.infomoney.com.br/feed/",
    "UOL Economia": "https://economia.uol.com.br/ultimas-noticias.rss",
    "Folha (Economia)": "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",
    "Canal Rural (Agro)": "https://www.canalrural.com.br/feed/",
    "Portal do Bitcoin": "https://portaldobitcoin.com.br/feed/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Reuters": "https://www.reuters.com/rssFeed/topNews",  # fallback generic feed
}


IMG_REGEX = re.compile(r'<img[^>]+src="([^">]+)"', re.I)

def extract_image_from_entry(entry):
    if 'media_content' in entry and entry.media_content:
        mc = entry.media_content[0]
        url = mc.get('url') if isinstance(mc, dict) else None
        if url: return url
    if 'media_thumbnail' in entry and entry.media_thumbnail:
        mt = entry.media_thumbnail[0]
        url = mt.get('url') if isinstance(mt, dict) else None
        if url: return url
    links = entry.get('links', []) or []
    for l in links:
        if l.get('rel') == 'enclosure' and l.get('type', '').startswith('image'):
            return l.get('href')
        if l.get('type', '').startswith('image'):
            return l.get('href')
    html = entry.get('summary', '') or entry.get('content', [{}])[0].get('value', '')
    m = IMG_REGEX.search(html)
    if m:
        return m.group(1)
    return None

def fetch_news(limit=8):
    results = []
    for source_name, url in RSS_SOURCES.items():
        try:
            f = feedparser.parse(url)
            entries = f.get("entries", [])[:limit]
            for e in entries:
                image = extract_image_from_entry(e)
                results.append({
                    "source": source_name,
                    "title": e.get("title", "")[:300],
                    "link": e.get("link", ""),
                    "published": e.get("published", "")[:120],
                    "image": image
                })
        except Exception:
            continue
    return results[:limit]

def aggregate_monthly(expenses):
    totals = {}
    for e in expenses:
        d = e['date'] if isinstance(e, dict) else e.date
        try:
            dt = datetime.fromisoformat(d)
        except Exception:
            try:
                dt = datetime.strptime(d, "%Y-%m-%d")
            except Exception:
                continue
        key = f"{dt.year}-{dt.month:02d}"
        totals.setdefault(key, 0.0)
        amt = float(e['amount'] if isinstance(e, dict) else e.amount)
        totals[key] += amt
    items = sorted(totals.items())
    return [{"key": k, "label": datetime.strptime(k, "%Y-%m").strftime("%b %Y"), "amount": v} for k, v in items]

def predict_next_month_total(expenses):
    months = aggregate_monthly(expenses)
    if len(months) < 2:
        return None
    X = np.array([[i] for i in range(len(months))])
    y = np.array([m['amount'] for m in months])
    model = LinearRegression().fit(X, y)
    next_index = np.array([[len(months)]])
    pred = float(model.predict(next_index)[0])
    print(pred)
    if pred < 0: pred=0
    return {"predicted": pred, "coef": float(model.coef_[0]), "intercept": float(model.intercept_), "months": months}

@app.route("/")
def index():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    expenses_json = [e.to_dict() for e in expenses]
    prediction = predict_next_month_total(expenses_json)
    return render_template("index.html",
                           initial_expenses=json.dumps(expenses_json),
                           initial_goal=json.dumps(0),
                           prediction=json.dumps(prediction),
                           news=json.dumps([]))

@app.route("/news")
def news_page():
    news = fetch_news(limit=20)
    return render_template("news.html", news=news or [])

@app.route("/api/news")
def api_news():
    limit = int(request.args.get("limit", 12))
    items = fetch_news(limit=limit)
    return jsonify(items)

@app.route("/api/expenses", methods=["GET", "POST"])
def api_expenses():
    if request.method == "GET":
        expenses = Expense.query.order_by(Expense.date.desc()).all()
        return jsonify([e.to_dict() for e in expenses])
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON required"}), 400
    date_str = data.get("date") or datetime.utcnow().strftime("%Y-%m-%d")
    try:
        if '/' in date_str:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            date_str = dt.strftime("%Y-%m-%d")
    except Exception:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
    e = Expense(description=data.get("description", ""),
                amount=float(data.get("amount", 0)),
                category=data.get("category", "Geral"),
                date=date_str)
    db.session.add(e)
    db.session.commit()
    return jsonify(e.to_dict()), 201

@app.route("/api/expenses/<int:eid>", methods=["DELETE"])
def api_delete(eid):
    e = Expense.query.get_or_404(eid)
    db.session.delete(e)
    db.session.commit()
    return "", 204

@app.route("/api/predict")
def api_predict():
    expenses = [e.to_dict() for e in Expense.query.all()]
    pred = predict_next_month_total(expenses)
    print(pred['predicted'])
    if pred['predicted']<0: pred['predicted']=0
    return jsonify(pred or {})

@app.route("/api/export_csv")
def api_export_csv():
    expenses = [e.to_dict() for e in Expense.query.order_by(Expense.date.desc()).all()]
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["id", "description", "amount", "category", "date"])
    for e in expenses:
        cw.writerow([e["id"], e["description"], e["amount"], e["category"], e["date"]])
    mem = io.BytesIO()
    mem.write(si.getvalue().encode("utf-8"))
    mem.seek(0)
    return send_file(mem, as_attachment=True, download_name="expenses.csv", mimetype="text/csv")

@app.route("/api/import_csv", methods=["POST"])
def api_import_csv():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "file required"}), 400
    stream = io.StringIO(file.stream.read().decode("utf-8"))
    reader = csv.DictReader(stream)
    created = 0
    for row in reader:
        try:
            date_str = row.get("date") or datetime.utcnow().strftime("%Y-%m-%d")
            if '/' in date_str:
                try:
                    dt = datetime.strptime(date_str, "%d/%m/%Y")
                    date_str = dt.strftime("%Y-%m-%d")
                except Exception:
                    pass
            e = Expense(description=row.get("description", ""), amount=float(row.get("amount", 0)), category=row.get("category", "Geral"), date=date_str)
            db.session.add(e)
            created += 1
        except Exception:
            continue
    db.session.commit()
    return jsonify({"imported": created})

@app.route("/report")
def report_pdf():
    expenses = [e.to_dict() for e in Expense.query.order_by(Expense.date.desc()).all()]
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("Relatório Financeiro — Sumário por Categoria", styles["Title"]))
    elements.append(Spacer(1, 12))

    total_sum = sum([e["amount"] for e in expenses]) if expenses else 0.0
    cat_map = {}
    for e in expenses:
        cat_map.setdefault(e["category"], 0.0)
        cat_map[e["category"]] += e["amount"]
    cat_rows = [["Categoria", "Total (R$)", "% do Total"]]
    for cat, val in sorted(cat_map.items(), key=lambda x: -x[1]):
        pct = (val / total_sum * 100) if total_sum > 0 else 0
        cat_rows.append([cat, f"{val:,.2f}", f"{pct:.2f}%"])
    table1 = Table(cat_rows, colWidths=[200, 150, 120])
    table1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b5fd7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))
    elements.append(table1)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("Detalhamento por Categoria", styles["Heading2"]))
    elements.append(Spacer(1, 8))
    detail_rows = [["Data", "Categoria", "Descrição", "Valor (R$)", "% da Categoria"]]
    for e in expenses:
        cat_total = cat_map.get(e["category"], 1)
        pct_cat = (e["amount"] / cat_total * 100) if cat_total > 0 else 0
        detail_rows.append([e["date"], e["category"], e["description"][:80], f"{e['amount']:,.2f}", f"{pct_cat:.2f}%"])
    table2 = Table(detail_rows, colWidths=[90, 120, 320, 100, 90])
    table2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b5fd7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))
    elements.append(table2)

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="relatorio_financeiro_detalhado.pdf", mimetype="application/pdf")

counter = Counter()

@app.route('/api/increment_counter')
def increment_counter():
    counter.increment()
    return {"count": counter.get_count()}


if __name__ == "__main__":
    app.run(debug=True, port=4025)