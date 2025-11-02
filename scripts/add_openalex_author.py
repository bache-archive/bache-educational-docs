#!/usr/bin/env python3
"""
Add `openalex_author: A5045900737` to front-matter of each
docs/educational/*/index.md if it's missing. Idempotent; makes .bak backups.
"""
import sys, re, shutil
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("ERROR: PyYAML not installed. Run:\n  python3 -m pip install pyyaml\n")
    sys.exit(1)

YAML_FENCE = re.compile(r"^---\s*$", re.M)
OPENALEX_ID = "A5045900737"
ROOT = Path(__file__).resolve().parents[1]
FILES = sorted(ROOT.glob("docs/educational/*/index.md"))

def split_front_matter(text: str):
    fences = [m.start() for m in YAML_FENCE.finditer(text)]
    if len(fences) >= 2 and text.startswith("---"):
        head_end = text.find("\n", fences[0]) + 1
        next_fence = YAML_FENCE.search(text, head_end)
        fm_str = text[head_end:next_fence.start()]
        body = text[next_fence.end():].lstrip("\n")
        meta = yaml.safe_load(fm_str) or {}
        return meta, body
    return {}, text

def join_front_matter(meta: dict, body: str) -> str:
    fm = yaml.safe_dump(meta, sort_keys=False).rstrip()
    return f"---\n{fm}\n---\n\n{body}"

def process(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    meta, body = split_front_matter(text)

    if meta.get("openalex_author"):
        return False  # no change

    meta["openalex_author"] = OPENALEX_ID
    shutil.copy2(path, f"{path}.bak")
    path.write_text(join_front_matter(meta, body), encoding="utf-8")
    return True

def main():
    if not FILES:
        print("No files found at docs/educational/*/index.md", file=sys.stderr)
        sys.exit(1)
    changed = 0
    for f in FILES:
        if process(f):
            print(f"✓ Added openalex_author → {f}")
            changed += 1
        else:
            print(f"• Already present → {f}")
    print(f"\nDone. Modified {changed} of {len(FILES)} files.")

if __name__ == "__main__":
    main()
