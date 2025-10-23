#!/usr/bin/env python3
"""
build_pages.py

Reusable builder: converts index.md (with YAML front matter) to index.html
for each topic in docs/educational/*/.

Improvements in this version:
- Header: single 'Home' button to the Educational Docs homepage (no Markdown / sources links).
- About card: simplified to a single 'About:' line and placed near the bottom (above Fair Use).
- Fair Use: injected only if the Markdown does not already contain a Fair Use section.
- Footer: 'Built by the Bache Archive' with Home linking to the Educational Docs homepage.
- Optional note near the subtitle to ensure 'LSD and the Mind of the Universe (LSDMU)' appears at least once.

Usage:
  python scripts/build_pages.py --root docs/educational --base-url /chris-bache-archive
  python scripts/build_pages.py --root docs/educational --topic future-human --base-url /chris-bache-archive
"""

from __future__ import annotations
import argparse, os, re
from typing import Dict, Tuple
import yaml
from markdown import markdown
from jinja2 import Template

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
LSDMU_PHRASE = "LSD and the Mind of the Universe (LSDMU)"

# Absolute homepage link for the footer and hero button
EDU_HOME = "https://bache-archive.github.io/bache-educational-docs/"

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{{ fm.title }} — Educational Topic</title>
  <link rel="canonical" href="{{ base_url }}/docs/educational/{{ fm.id }}/" />
  <meta name="description" content="Readable, styled pages from the Bache Archive." />
  <link rel="stylesheet" href="{{ base_url }}/assets/style.css">
</head>
<body>
  <div class="container">
<header class="hero" aria-labelledby="page-title">
  <span class="pill">Educational Topic</span>
  <h1 id="page-title" class="title">{{ fm.title }}</h1>
  <p class="subtitle">
    What does <strong>Chris Bache</strong> say about <strong>{{ fm.title }}</strong>? 
    {% if needs_lsdmu_note %}This page references <strong>{{ lsdmu_phrase }}</strong>.{% endif %}
  </p>
  <div class="btnrow">
    <a class="btn" href="{{ edu_home }}">Home</a>
  </div>
</header>

<section class="section">
  <div class="md card">
    {{ body_html }}
  </div>
</section>

{# --- About card placed near bottom, simplified to a single line --- #}
{% if about_text %}
<section class="section doc-meta" aria-labelledby="doc-meta-title">
  <div class="card">
    <h2 id="doc-meta-title">About this document</h2>
    <p><strong>About:</strong> {{ about_text }}</p>
  </div>
</section>
{% endif %}

{# --- Fair Use card (only if not already present in the content) --- #}
{% if not has_fair_use %}
{% set fair_use_text = fm.fair_use or
  'Excerpts from <em>LSD and the Mind of the Universe</em> are reproduced here under the fair use doctrine for ' ~
  '<strong>educational and scholarly purposes</strong>. They support study, research, and public understanding of ' ~
  'Christopher M. Bache’s work. All quotations remain the intellectual property of their respective rights holders.' %}

<section class="section">
  <div class="card">
    <h2>Fair Use Notice</h2>
    <p>{{ fair_use_text | safe }}</p>
  </div>
</section>
{% endif %}

    <div class="footer muted">
      Built by the Bache Archive · <a href="{{ edu_home }}">Home</a>
    </div>
  </div>
</body>
</html>
"""

def read(p: str) -> str:
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def write(p: str, s: str) -> None:
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)

def parse_md(md: str) -> Tuple[Dict, str]:
    """Return (front_matter_dict, markdown_body)."""
    m = FRONT_MATTER_RE.search(md)
    if not m:
        return {}, md
    fm = yaml.safe_load(m.group(1)) or {}
    if not isinstance(fm, dict):
        fm = {}
    return fm, md[m.end():]

def needs_lsdmu_note_func(fm: Dict, body_md: str) -> bool:
    hay = ((fm.get("about") or "") + " " + body_md).lower()
    return LSDMU_PHRASE.lower() not in hay

def contains_fair_use(body_md: str, body_html: str) -> bool:
    """
    Detect if the Markdown/HTML already contains a 'Fair Use' section.
    - Matches headings like '## Fair Use', '## Fair Use Notice', case-insensitive.
    - Also checks rendered HTML for <h2>…Fair Use…</h2>.
    """
    md_head_re = re.compile(r"^\s{0,3}#{2,6}\s+fair\s+use(\s+notice)?\b", re.I | re.M)
    if md_head_re.search(body_md):
        return True
    html_head_re = re.compile(r"<h[1-6][^>]*>\s*fair\s+use(\s+notice)?\s*</h[1-6]>", re.I)
    if html_head_re.search(body_html):
        return True
    return False

def render_html(fm: Dict, body_md: str, base_url: str) -> str:
    # Ensure an id exists
    if not fm.get("id"):
        fm["id"] = (fm.get("title") or "topic").strip().lower().replace(" ", "-")

    # Render Markdown body
    body_html = markdown(
        body_md,
        extensions=[
            "extra",
            "sane_lists",
            "attr_list",
            "footnotes",
            "toc",
            "md_in_html",
        ],
        output_format="xhtml",
    )

    # About text: prefer front matter 'about', else None (no About card)
    about_text = (fm.get("about") or "").strip()
    if not about_text:
        about_text = None

    tmpl = Template(HTML_TEMPLATE)
    html = tmpl.render(
        fm=fm,
        body_html=body_html,
        base_url=base_url.rstrip("/"),
        lsdmu_phrase=LSDMU_PHRASE,
        needs_lsdmu_note=needs_lsdmu_note_func(fm, body_md),
        has_fair_use=contains_fair_use(body_md, body_html),
        about_text=about_text,
        edu_home=EDU_HOME,
    )
    return html

def build_topic(folder: str, base_url: str) -> str:
    md_path = os.path.join(folder, "index.md")
    if not os.path.exists(md_path):
        return f"!! {os.path.basename(folder)}: index.md missing"

    fm, body = parse_md(read(md_path))
    html = render_html(fm, body, base_url=base_url)
    write(os.path.join(folder, "index.html"), html)
    return f"✓ {os.path.basename(folder)}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Path to docs/educational")
    ap.add_argument("--topic", help="Build only this topic folder name")
    ap.add_argument("--base-url", default="/chris-bache-archive", help="Base URL for canonical + CSS")
    args = ap.parse_args()

    root = args.root.rstrip("/")
    if args.topic:
        folders = [os.path.join(root, args.topic)]
    else:
        folders = [
            os.path.join(root, d)
            for d in sorted(os.listdir(root))
            if os.path.isdir(os.path.join(root, d))
        ]

    for folder in folders:
        print(build_topic(folder, base_url=args.base_url))

if __name__ == "__main__":
    main()