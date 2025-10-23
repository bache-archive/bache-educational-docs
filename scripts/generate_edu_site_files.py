#!/usr/bin/env python3
import sys, re
from pathlib import Path
from urllib.parse import quote
from datetime import datetime, timezone

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://bache-archive.github.io/bache-educational-docs").rstrip("/")

REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = REPO_ROOT  # we serve from repo root on Pages (main /)

def abs_url(rel_path: str) -> str:
    return BASE + "/" + quote(rel_path.lstrip("/"), safe="/")

def lastmod_for(p: Path) -> str | None:
    try:
        ts = p.stat().st_mtime
        return datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
    except Exception:
        return None

def collect_topics():
    base = REPO_ROOT / "docs" / "educational"
    topics = []
    if base.exists():
        for d in sorted([p for p in base.iterdir() if p.is_dir()]):
            idx = d / "index.html"
            if idx.exists():
                topics.append(d.name)
    return topics

def write_index_html(topics):
    head = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Educational Documents — Chris Bache</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="assets/style.css">
<body>
<header><h1>Educational Documents</h1><p>Topic index</p></header>
<main><ul>
"""
    items = []
    for t in topics:
        items.append(f'  <li><a href="docs/educational/{t}/">{t.replace("-", " ").title()}</a></li>')
    tail = """</ul></main>
<footer><p>&copy; Bache Archive. Educational materials are fair-use commentary. See <a href="LEGAL_NOTICE.md">LEGAL_NOTICE.md</a>.</p></footer>
</body></html>
"""
    (REPO_ROOT / "index.html").write_text(head + "\n".join(items) + tail, encoding="utf-8")

def write_robots():
    txt = f"""User-agent: *
Allow: /

Sitemap: {BASE}/sitemap.xml
"""
    (REPO_ROOT / "robots.txt").write_text(txt, encoding="utf-8")

def write_nojekyll():
    (REPO_ROOT / ".nojekyll").write_text("", encoding="utf-8")

def write_sitemap(topics):
    urls = []
    # optional: include site root
    urls.append(("/", lastmod_for(REPO_ROOT / "index.html")))
    for t in topics:
        rel = f"docs/educational/{t}/index.html"
        urls.append((rel, lastmod_for(REPO_ROOT / rel)))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for rel, lm in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{abs_url(rel)}</loc>")
        if lm:
            lines.append(f"    <lastmod>{lm}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>\n")
    (REPO_ROOT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")

def main():
    topics = collect_topics()
    write_index_html(topics)
    write_robots()
    write_nojekyll()
    write_sitemap(topics)
    print(f"Generated: index.html, robots.txt, .nojekyll, sitemap.xml ({len(topics)} topics)")

if __name__ == "__main__":
    main()
