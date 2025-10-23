#!/usr/bin/env python3
import re, glob, io

NEW_CITE = ("Cite as: Bache Archive — Educational Docs Edition (2025). "
            "Based on the works of Christopher M. Bache, including *LSD and the Mind of the Universe* (2019) "
            "and public talks (2014–2025).")

# --- Regexes ---
# Remove "Built from sources.json ..." (Markdown)
RX_BUILT_MD = re.compile(r"^Built from\s+`?sources\.json`?.*$\n?", re.M)
# Remove "Built from ... sources.json ..." (HTML <p>…</p>)
RX_BUILT_HTML_P = re.compile(r"<p>[^<]*Built from[^<]*sources\.json[^<]*</p>\s*", re.I)

# Replace any "Cite as: ..." (Markdown or plain text in HTML) with NEW_CITE
RX_CITE_ANY = re.compile(r"Cite\s+as:[^\n<]*", re.I)

# Remove legacy RAG tail if present anywhere
RX_OLD_RAG = re.compile(
    r"Christopher M\. Bache\s+—\s+Public Talks\s*\(2014–2025\)[^.<\n]*"
    r"(?:,?\s*retrieved[^.<\n]*)?\.*", re.I
)

def clean_text(text: str, is_html: bool) -> str:
    # 1) drop "Built from sources.json ..."
    if is_html:
        text = RX_BUILT_HTML_P.sub("", text)
    text = RX_BUILT_MD.sub("", text)

    # 2) remove old RAG tail
    text = RX_OLD_RAG.sub("", text)

    # 3) normalize/replace any existing "Cite as:" with NEW_CITE
    if "Cite as:" in text or re.search(RX_CITE_ANY, text):
        text = RX_CITE_ANY.sub(NEW_CITE, text)
    else:
        # If no cite line exists at all, try to add it to a likely Provenance section
        # Insert after a Provenance header if present, else append at end.
        m = re.search(r"(?im)^(##+\s+provenance\s*)$", text)
        if m:
            insert_at = m.end()
            text = text[:insert_at] + "\n\n" + NEW_CITE + "\n" + text[insert_at:]
        else:
            # HTML: add before closing card/container if possible; otherwise append.
            if is_html and "</div>\n</section>" in text:
                text = text.replace("</div>\n</section>", f"<p>{NEW_CITE}</p>\n</div>\n</section>", 1)
            else:
                text = text.rstrip() + "\n\n" + NEW_CITE + "\n"

    # 4) dedupe if NEW_CITE repeated
    text = re.sub(r"(?:%s\s*){2,}" % re.escape(NEW_CITE), NEW_CITE + "\n", text)

    return text

def main():
    paths = []
    paths += glob.glob("docs/educational/*/index.md")
    paths += glob.glob("docs/educational/*/index.html")

    for p in sorted(paths):
        with io.open(p, "r", encoding="utf-8") as f:
            raw = f.read()
        cleaned = clean_text(raw, p.endswith(".html"))
        if cleaned != raw:
            with io.open(p, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print(f"✓ cleaned {p}")
        else:
            print(f"= no change {p}")

if __name__ == "__main__":
    main()
