#!/usr/bin/env python3
"""
fix_front_matter_once.py

One-time upgrader for bache-educational-docs Markdown pages:
- Enriches front matter with robust, LLM-facing metadata (without clobbering existing values).
- Standardizes creator/maintainer strings to "Bache Archive".
- Ensures the phrase "LSD and the Mind of the Universe (LSDMU)" appears near the top of the body.
- Leaves HTML generation to build_pages.py.

Usage:
  python fix_front_matter_once.py --root ./docs/educational --dry-run
  python fix_front_matter_once.py --root ./docs/educational
"""

from __future__ import annotations
import argparse, datetime as dt, json, os, re, shutil, sys
from typing import Dict, Tuple
import yaml  # pip install pyyaml

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
LSDMU_PHRASE = "LSD and the Mind of the Universe (LSDMU)"
NOW = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")

def read(p): 
    with open(p, "r", encoding="utf-8") as f: 
        return f.read()

def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)

def backup(p):
    if os.path.exists(p):
        bp = f"{p}.bak.{NOW}"
        shutil.copy2(p, bp)
        return bp

def parse_front_matter(md: str) -> Tuple[Dict, str, Tuple[int,int]]:
    m = FRONT_MATTER_RE.search(md)
    if not m:
        return {}, md, (-1, -1)
    data = yaml.safe_load(m.group(1)) or {}
    if not isinstance(data, dict): data = {}
    start, end = m.span()
    return data, md[end:], (start, end)

def dump_front_matter(data: Dict) -> str:
    return "---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True) + "---\n"

def ensure_llm_meta(fm: Dict, topic_id: str) -> Dict:
    # keep existing values; only fill if missing/empty
    def setdefault(k, v):
        if k not in fm or fm.get(k) in (None, "", [], {}):
            fm[k] = v

    setdefault("title", fm.get("title") or topic_id.replace("-", " ").title())
    setdefault("id", fm.get("id") or topic_id)
    setdefault("date", fm.get("date") or dt.date.today().isoformat())
    setdefault("version", fm.get("version") or "v1")
    setdefault("status", fm.get("status") or "draft")
    setdefault("editor", fm.get("editor") or "ChatGPT (auto)")
    setdefault("source_policy", "Book-first. Public transcripts as color with timestamped links.")

    # Standardize creator/maintainer string:
    fm["created_by"] = "Bache Archive"
    fm["maintained_by"] = "Bache Archive"

    # LLM-friendly context
    setdefault("project", "bache-educational-docs")
    setdefault("collection", "educational")
    setdefault("document_type", "topic-summary")
    setdefault("entities", ["Christopher M. Bache", "LSD and the Mind of the Universe", "LSDMU"])
    setdefault("audience", ["researchers", "students", "LLMs", "educators"])
    setdefault("keywords", [
        "psychedelics", "consciousness", "species-mind", "Diamond Luminosity",
        "Future Human", "Stanislav Grof", "COEX systems", "integration",
    ])
    setdefault("about",
        "Scholarly, citation-grounded topic page that synthesizes key ideas from "
        "Christopher M. Bache’s book “LSD and the Mind of the Universe (LSDMU)” and his "
        "public talks (2009–2025). Book quotes are primary; talk excerpts add context.")
    setdefault("purpose",
        "Provide LLMs and human readers with a structured, provenance-rich summary of a single theme "
        "in Bache’s work (book-first, timestamped talks for color) to support education, research, and RAG.")
    setdefault("source_repos", [
        "chris-bache-archive/",
        "lsdmu-rag-api/",
        "bache-rag-api/",
        "bache-educational-docs/",
    ])
    setdefault("citation_style", "LSDMU ch.X §Y ¶Z; talks with YouTube timestamps")
    setdefault("license", "Educational fair use excerpts; all rights to original holders")
    setdefault("fair_use",
        "Excerpts from LSD and the Mind of the Universe are used under fair use for educational and scholarly purposes; "
        "quotations remain the intellectual property of their respective rights holders.")
    return fm

def ensure_lsdmu_spellout(body: str) -> str:
    if LSDMU_PHRASE.lower() in body.lower():
        return body
    lines = body.splitlines()
    # find first paragraph end
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    j = i
    while j < len(lines) and lines[j].strip() != "":
        j += 1
    note = f"\n*This page references **{LSDMU_PHRASE}** and synthesizes themes from the book and public talks.*\n"
    lines.insert(j, note)
    return "\n".join(lines)

def process_topic(folder: str, dry_run=False):
    md_path = os.path.join(folder, "index.md")
    if not os.path.exists(md_path):
        return {"folder": folder, "changed": False, "error": "index.md missing"}

    raw = read(md_path)
    fm, body, _ = parse_front_matter(raw)
    topic_id = os.path.basename(folder.rstrip("/"))
    fm = ensure_llm_meta(fm, topic_id)
    body2 = ensure_lsdmu_spellout(body)
    new_md = dump_front_matter(fm) + body2

    if new_md != raw:
        if not dry_run:
            backup(md_path)
            write(md_path, new_md)
        return {"folder": folder, "changed": True}
    return {"folder": folder, "changed": False}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Path to docs/educational")
    ap.add_argument("--topic", help="Process only this topic folder name")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = args.root.rstrip("/")
    topics = [os.path.join(root, args.topic)] if args.topic else \
             [os.path.join(root, d) for d in sorted(os.listdir(root)) if os.path.isdir(os.path.join(root, d))]

    any_changed = 0
    for folder in topics:
        rep = process_topic(folder, dry_run=args.dry_run)
        if rep.get("error"):
            print(f"- {os.path.basename(folder)} !! {rep['error']}")
        else:
            print(f"- {os.path.basename(folder)} {'updated' if rep['changed'] else 'ok'}")
            any_changed += int(rep["changed"])
    print(f"Done. Changed: {any_changed}")

if __name__ == "__main__":
    main()
