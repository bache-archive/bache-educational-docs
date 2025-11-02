#!/usr/bin/env python3
import re, glob

new_line = ("Cite as: Bache Archive — Educational Docs Edition (2025). "
            "Based on the works of Christopher M. Bache, including *LSD and the Mind of the Universe* (2019) "
            "and public talks (2009–2025).")

targets = glob.glob("docs/educational/*/index.md") + glob.glob("docs/educational/*/index.html")
pattern = re.compile(r"Cite\s+as:[^\n<]+(?:retrieved[^\n<]*)?", re.I)

for path in targets:
    text = open(path, encoding="utf-8").read()
    if "Cite as:" in text:
        new_text = pattern.sub(new_line, text)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"✓ updated {path}")
