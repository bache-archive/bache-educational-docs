#!/usr/bin/env python3
# v3.3-wikidata-integration — add wikidata_author and related_works to topic front-matter
# - Non-destructive: only adds missing fields; preserves curated values
# - Creates timestamped .bak alongside any modified file
# - Requires: ruamel.yaml

import re
import time
import pathlib
import sys
from io import StringIO
from ruamel.yaml import YAML

# Canonical QIDs (from bache-archive-meta/wikidata.jsonld)
AUTHOR_QID = "Q112496741"  # Christopher M. Bache
RELATED_QIDS = ["Q136684740", "Q136684765", "Q136684793", "Q136684807"]

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "docs" / "educational").glob("*/index.md"))  # <-- fixed glob

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=2, offset=2)
yaml.explicit_start = False
yaml.explicit_end = False

DELIM = r"^---\s*$"

def split_front_matter(text: str):
    """
    Returns (yaml_text, body) if front-matter found, else (None, original_text).
    Accepts leading BOM or whitespace before the first '---'.
    """
    # normalize possible BOM
    if text.startswith("\ufeff"):
        text_ = text.lstrip("\ufeff")
    else:
        text_ = text

    # must start with '---' (possibly after newlines/whitespace)
    if not re.match(r"^\s*---\s*$", text_.splitlines()[0] if text_.splitlines() else ""):
        return None, text

    parts = re.split(DELIM, text_, maxsplit=2, flags=re.M)
    # parts shape: ['', <yaml>, <body>] (possible leading empty due to split)
    if len(parts) < 3:
        return None, text
    # Preserve original leading whitespace/BOM by extracting from original
    head, yaml_block, body = parts[0], parts[1], parts[2]
    # `head` is usually '' because we matched at start; keep original text's leading BOM if present
    return (yaml_block.strip() + "\n"), body.lstrip("\n")

def join_front_matter(yaml_text: str, body: str) -> str:
    return f"---\n{yaml_text}---\n{body}"

def ensure_fields(meta: dict) -> bool:
    """
    Adds fields only if missing. Does NOT overwrite curated values.
    Returns True if any changes were made.
    """
    changed = False

    if "wikidata_author" not in meta or meta.get("wikidata_author") in (None, ""):
        meta["wikidata_author"] = AUTHOR_QID
        changed = True

    if "related_works" not in meta or meta.get("related_works") in (None, []):
        # Default list; do not merge into existing curated arrays
        meta["related_works"] = RELATED_QIDS[:]
        changed = True

    return changed

def main():
    updated = 0
    skipped = 0
    no_front_matter = 0

    for path in FILES:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Read error: {path} -> {e}", file=sys.stderr)
            skipped += 1
            continue

        fm_text, body = split_front_matter(text)
        if fm_text is None:
            no_front_matter += 1
            continue

        try:
            meta = yaml.load(fm_text) or {}
            if not isinstance(meta, dict):
                print(f"YAML root is not a mapping: {path}", file=sys.stderr)
                skipped += 1
                continue
        except Exception as e:
            print(f"YAML parse error in {path}: {e}", file=sys.stderr)
            skipped += 1
            continue

        changed = ensure_fields(meta)
        if not changed:
            skipped += 1
            continue

        # Backup before writing
        ts = time.strftime("%Y-%m-%d_%H%M%S")
        backup = path.with_suffix(f".md.bak.{ts}")
        try:
            backup.write_text(text, encoding="utf-8")
        except Exception as e:
            print(f"Backup write error: {backup} -> {e}", file=sys.stderr)
            skipped += 1
            continue

        # Dump YAML back
        buf = StringIO()
        yaml.dump(meta, buf)
        new_text = join_front_matter(buf.getvalue(), body)

        try:
            path.write_text(new_text, encoding="utf-8")
            updated += 1
            print(f"Updated: {path}")
        except Exception as e:
            print(f"Write error: {path} -> {e}", file=sys.stderr)
            skipped += 1

    print(f"\nSummary: updated={updated}, skipped={skipped}, no_front_matter={no_front_matter}")

if __name__ == "__main__":
    main()