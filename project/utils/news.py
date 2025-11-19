import feedparser
import re
from datetime import datetime

# Regex para encontrar imagens em descrições HTML
IMG_REGEX = re.compile(r'<img[^>]+src="([^">]+)"', re.I)

# Fontes de RSS (As mesmas do seu código antigo)
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
    "Reuters": "https://www.reuters.com/rssFeed/topNews",
}


def extract_image_from_entry(entry):
    """Tenta extrair URL da imagem de várias tags RSS."""
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

    # Tenta extrair do HTML do summary ou content
    html = entry.get('summary', '')
    if 'content' in entry:
        for c in entry.content:
            html += c.get('value', '')

    m = IMG_REGEX.search(html)
    if m:
        return m.group(1)
    return None


def fetch_news(limit=20):
    """Busca e normaliza notícias de todas as fontes."""
    results = []
    for source_name, url in RSS_SOURCES.items():
        try:
            f = feedparser.parse(url)
            # Pega apenas as 5 primeiras de cada fonte para não sobrecarregar
            entries = f.get("entries", [])[:5]
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

    # Embaralha um pouco ou ordena? Por enquanto vamos retornar a lista bruta
    # O ideal seria ordenar por data, mas formatos de data RSS variam muito.
    return results[:limit]