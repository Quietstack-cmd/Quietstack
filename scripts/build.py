#!/usr/bin/env python3
"""
Génère le site statique dans docs/ à partir des articles markdown
présents dans content/articles/. Un article n'est publié que si sa
date de publication (front matter) est passée ou égale à aujourd'hui.

Aucune dépendance externe : uniquement la bibliothèque standard,
pour que ce script tourne sans installation particulière dans
GitHub Actions.
"""
import re
import datetime
import pathlib
import html

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content" / "articles"
TEMPLATES_DIR = ROOT / "templates"
OUT_DIR = ROOT / "docs"
CSS_SRC = ROOT / "assets" / "css" / "style.css"

SITE_TITLE = "Quietstack"
SITE_DESCRIPTION = "Guides pratiques sur les bureaux assis-debout et l'ergonomie du télétravail."


def read(path):
    return path.read_text(encoding="utf-8")


def parse_front_matter(text):
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError("Front matter manquant")
    raw_meta, body = match.groups()
    meta = {}
    for line in raw_meta.splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        value = value.strip().strip('"')
        meta[key.strip()] = value
    return meta, body.strip()


def inline_markdown(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def markdown_to_html(body):
    lines = body.splitlines()
    html_parts = []
    paragraph = []
    list_items = []

    def flush_paragraph():
        if paragraph:
            html_parts.append("<p>" + inline_markdown(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    def flush_list():
        if list_items:
            items = "".join(f"<li>{inline_markdown(i)}</li>" for i in list_items)
            html_parts.append(f"<ul>{items}</ul>")
            list_items.clear()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            flush_paragraph()
            flush_list()
            html_parts.append(f"<h2>{inline_markdown(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            flush_paragraph()
            flush_list()
            html_parts.append(f"<h1>{inline_markdown(stripped[2:])}</h1>")
        elif stripped.startswith("- "):
            flush_paragraph()
            list_items.append(stripped[2:])
        elif stripped == "":
            flush_paragraph()
            flush_list()
        else:
            paragraph.append(stripped)

    flush_paragraph()
    flush_list()
    return "\n".join(html_parts)


def load_articles():
    articles = []
    for path in sorted(CONTENT_DIR.glob("*.md")):
        meta, body = parse_front_matter(read(path))
        meta["date_obj"] = datetime.date.fromisoformat(meta["date"])
        meta["body_html"] = markdown_to_html(body)
        articles.append(meta)
    return articles


def render_page(title, description, body_html, root_prefix=""):
    header = read(TEMPLATES_DIR / "header.html").replace("__ROOT__", root_prefix)
    footer = read(TEMPLATES_DIR / "footer.html")
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="stylesheet" href="{root_prefix}assets/css/style.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
</head>
<body>
{header}
{body_html}
{footer}
</body>
</html>
"""


def hero_svg():
    return """
    <svg viewBox="0 0 300 320" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Schéma coté d'un poste de bureau assis-debout">
      <rect x="40" y="230" width="140" height="10" fill="#1B2A4A"/>
      <rect x="46" y="240" width="8" height="60" fill="#1B2A4A"/>
      <rect x="166" y="240" width="8" height="60" fill="#1B2A4A"/>
      <circle cx="70" cy="150" r="16" fill="#1B2A4A"/>
      <rect x="60" y="168" width="20" height="58" fill="#1B2A4A"/>
      <line x1="220" y1="150" x2="220" y2="230" stroke="#D9822B" stroke-width="2"/>
      <line x1="212" y1="150" x2="228" y2="150" stroke="#D9822B" stroke-width="2"/>
      <line x1="212" y1="230" x2="228" y2="230" stroke="#D9822B" stroke-width="2"/>
      <text x="235" y="194" font-family="IBM Plex Mono, monospace" font-size="12" fill="#7A4712">108 cm</text>
      <line x1="20" y1="60" x2="20" y2="150" stroke="#C7D0CE" stroke-width="1.5" stroke-dasharray="4 3"/>
      <line x1="12" y1="150" x2="28" y2="150" stroke="#C7D0CE" stroke-width="1.5"/>
      <text x="0" y="55" font-family="IBM Plex Mono, monospace" font-size="11" fill="#4A5875">yeux</text>
    </svg>
    """


def build_home(articles):
    today = datetime.date.today()
    published = [a for a in articles if a["date_obj"] <= today]
    published.sort(key=lambda a: a["date_obj"], reverse=True)

    hero = f"""
    <section class="hero">
      <div>
        <h1>Bien régler son poste de télétravail, sans y laisser son dos.</h1>
        <p>{html.escape(SITE_DESCRIPTION)} Des guides concrets, basés sur des repères vérifiables, pas sur des promesses marketing.</p>
      </div>
      <div class="hero-figure">{hero_svg()}</div>
    </section>
    """

    if published:
        cards = []
        for a in published:
            cards.append(f"""
            <a class="article-card" href="articles/{a['slug']}.html">
              <div class="article-meta">
                <span class="cat">{html.escape(a['category'])}</span>
                <span class="time">{html.escape(a['read_time'])}</span>
              </div>
              <h2 class="article-title">{html.escape(a['title'])}</h2>
              <p class="article-excerpt">{html.escape(a['excerpt'])}</p>
            </a>
            """)
        list_html = "".join(cards)
    else:
        list_html = '<p class="empty-note">Premier article en préparation — publication automatique sous peu.</p>'

    upcoming = [a for a in articles if a["date_obj"] > today]
    upcoming_note = ""
    if upcoming:
        upcoming.sort(key=lambda a: a["date_obj"])
        next_date = upcoming[0]["date_obj"].strftime("%d/%m/%Y")
        upcoming_note = f'<p class="empty-note">Prochain article programmé pour le {next_date}.</p>'

    body = f"""
    {hero}
    <div class="wrap" style="max-width:900px;">
      <p class="section-label">Derniers articles</p>
      <div class="article-list">
        {list_html}
      </div>
      {upcoming_note}
    </div>
    """
    html_out = render_page(
        f"{SITE_TITLE} — Ergonomie du télétravail",
        SITE_DESCRIPTION,
        body,
        root_prefix="",
    )
    (OUT_DIR / "index.html").write_text(html_out, encoding="utf-8")


def build_article(article):
    body = f"""
    <article class="article-page">
      <a class="back-link" href="../index.html">&larr; retour aux articles</a>
      <div class="article-meta">
        <span class="cat">{html.escape(article['category'])}</span>
        <span class="time">{html.escape(article['read_time'])}</span>
      </div>
      <h1>{html.escape(article['title'])}</h1>
      <div class="article-body">
        {article['body_html']}
      </div>
      <div class="article-footer-note">
        Cet article contient parfois des liens affiliés vers des produits mentionnés. Cela ne change rien au prix payé, et nous ne recommandons que ce qui nous semble réellement utile.
      </div>
    </article>
    """
    html_out = render_page(
        f"{article['title']} — {SITE_TITLE}",
        article["excerpt"],
        body,
        root_prefix="../",
    )
    out_path = OUT_DIR / "articles" / f"{article['slug']}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_out, encoding="utf-8")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "assets" / "css").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "assets" / "css" / "style.css").write_text(read(CSS_SRC), encoding="utf-8")

    articles = load_articles()
    today = datetime.date.today()

    build_home(articles)
    for article in articles:
        if article["date_obj"] <= today:
            build_article(article)

    published_count = sum(1 for a in articles if a["date_obj"] <= today)
    print(f"Build terminé : {published_count}/{len(articles)} articles publiés.")


if __name__ == "__main__":
    main()
