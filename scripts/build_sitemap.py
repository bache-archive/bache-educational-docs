#!/usr/bin/env python3
"""
build_sitemap.py

Generates sitemap.xml for GitHub Pages.
- Includes homepage
- Includes each topic under docs/educational/*/
- Uses file mtimes for <lastmod>
- Respects your GitHub Pages base URL
"""

from __future__ import annotations
import os, time, argparse, xml.sax.saxutils as sx

BASE_URL = "https://bache-archive.github.io/bache-educational-docs"

def iso8601(ts: float) -> str:
    return time.strftime("%Y-%m-%d", time.gmtime(ts))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="docs/educational", help="Path to topics root (default: docs/educational)")
    ap.add_argument("--out", default="sitemap.xml", help="Output path (default: sitemap.xml in repo root)")
    ap.add_argument("--base-url", default=BASE_URL, help="Public site base URL")
    args = ap.parse_args()

    root = args.root.rstrip("/")

    urls = []

    # 1) Homepage
    try:
        mtime = os.path.getmtime("index.html")
    except FileNotFoundError:
        mtime = time.time()
    urls.append({
        "loc": f"{args.base_url}/",
        "lastmod": iso8601(mtime),
        "changefreq": "weekly",
        "priority": "1.0",
    })

    # 2) Topic pages
    if os.path.isdir(root):
        for name in sorted(os.listdir(root)):
            topic_dir = os.path.join(root, name)
            if not os.path.isdir(topic_dir):
                continue
            # canonical topic URL ends with a trailing slash
            loc = f"{args.base_url}/docs/educational/{sx.quoteattr(name)[1:-1]}/"
            idx = os.path.join(topic_dir, "index.html")
            try:
                mtime = os.path.getmtime(idx)
            except FileNotFoundError:
                mtime = time.time()
            urls.append({
                "loc": loc,
                "lastmod": iso8601(mtime),
                "changefreq": "monthly",
                "priority": "0.7",
            })

    # 3) Serialize XML
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for u in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{sx.escape(u['loc'])}</loc>")
        lines.append(f"    <lastmod>{u['lastmod']}</lastmod>")
        lines.append(f"    <changefreq>{u['changefreq']}</changefreq>")
        lines.append(f"    <priority>{u['priority']}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>\n")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✓ Wrote {args.out} with {len(urls)} URLs.")

if __name__ == "__main__":
    main()
