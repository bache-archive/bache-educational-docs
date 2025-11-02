PROVENANCE.md

# Provenance — Bache Educational Docs v1.0.0

**Repository:** https://github.com/bache-archive/bache-educational-docs  
**Release:** v1.0.0 — Initial Public Release  
**Release Date:** 2025-10-29  
**Curator:** Bache Archive Project  
**License:** Creative Commons BY-NC-SA 4.0  
**Zenodo DOI:** *(pending)*  
**Internet Archive Identifier:** bache-educational-docs-v1-0-0  

---

## 1 · Purpose

This release establishes the first canonical, versioned edition of the **Bache Educational Docs**, a public collection of educational pages that synthesize and contextualize the ideas of **Christopher M. Bache**—especially as expressed in *LSD and the Mind of the Universe (2019)* and his public talks (2009–2025).

Each document is designed for long-term scholarly reference and machine-assisted interpretation, providing a bridge between Bache’s written and spoken work.

---

## 2 · Contents

Included directories and files:

| Path | Description |
|------|--------------|
| `docs/educational/` | Markdown and rendered HTML pages for each topic (e.g., *Future Human*, *Diamond Luminosity*, *Species Mind*). |
| `assets/` | CSS and shared layout resources used by the published GitHub Pages site. |
| `index.html`, `sitemap.xml`, `robots.txt` | Static site entry points for the educational collection. |
| `README.md`, `LICENSE.md`, `LEGAL_NOTICE.md`, `CHANGELOG.md` | Core documentation, licensing, and version history. |
| `PROVENANCE.md` | This provenance statement. |
| *(optional)* `checksums/sha256sum_v1.0.0.txt` | Cryptographic integrity list for verifying file authenticity. |

Excluded from this archival release are build scripts, quote-pack harvest reports, and temporary backups (`*.bak.*`), which remain preserved in the GitHub repository for transparency but are not part of the public educational corpus.

---

## 3 · Generation Method

All pages were generated from verified Markdown sources using internal Python build scripts (`build_pages.py`, `generate_edu_site_files.py`) that render standardized HTML.  
The process follows the documented workflow in `scripts/` and `tools/` and preserves consistent metadata headers (YAML front matter) across all topics.

Each educational document adheres to a book-first structure:

1. **Curated Weave** — paraphrased synthesis anchored in *LSDMU* citations.  
2. **Supporting Transcript Quotes** — timestamped excerpts from verified public talks.  
3. **Notes & Synthesis** — interpretive commentary.  
4. **Provenance & Fair Use Notice** — citation and licensing clarity.

---

## 4 · Verification

To verify the integrity of this release:

```bash
sha256sum --check checksums/sha256sum_v1.0.0.txt

All listed files should return OK.
For long-term fixity, identical checksums are mirrored on Zenodo and the Internet Archive.

⸻

5 · Lineage and Related Repositories

This release forms part of the Chris Bache Archive ecosystem:
	•	bache-rag-api — Vector index of public talks.
	•	lsdmu-rag-api — Paragraph-level embeddings of LSD and the Mind of the Universe.
	•	lsdmu-bibliography — Machine-readable bibliographic corpus.
	•	chris-bache-archive — Full transcript and fixity archive.

Together these repositories form a coherent digital infrastructure for the preservation and semantic study of Christopher M. Bache’s philosophy.

⸻

6 · Fair-Use and Educational Intent

All textual material in this repository is reproduced or paraphrased under U.S. fair-use principles for educational and scholarly purposes.
The work is licensed under CC BY-NC-SA 4.0, permitting non-commercial reuse with attribution and share-alike requirements.

⸻

7 · Citation

When referencing this release:

Bache Archive Project. “Bache Educational Docs (v1.0.0).”
GitHub, Zenodo, and Internet Archive, 2025. CC BY-NC-SA 4.0.
https://bache-archive.github.io/bache-educational-docs/

⸻

End of Provenance Statement

