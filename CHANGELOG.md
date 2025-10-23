# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project uses date-based versions (`YYYY-MM-DD`).

## [2025-10-23] — Educational Docs refresh
### Added
- Modernized homepage with hero, search/filter, and responsive topic cards using shared `assets/style.css`.
- Google Search Console verification file at repository root (`googleb87f06a4d8a4ae9e.html`).
- `scripts/fix_front_matter_once.py` — one-time front-matter upgrader for Markdown.
- `scripts/build_pages.py` — reusable Markdown → HTML builder (book-first, visible Fair Use).
- `assets/style.css` — shadcn-inspired theme consolidated for all pages.
- `robots.txt`, `sitemap.xml`, and `.nojekyll` for GitHub Pages.

### Changed
- All topic pages now include a concise **About** card and an **always-visible Fair Use** section.
- Footer updated to: **“Built by the Bache Archive”** with **Home** linking to the public site.
- Front matter enriched for LLMs/humans: `project`, `collection`, `document_type`, `about`, `purpose`, etc.
- Home and topic pages consistently reference the full book title at least once:
  *“LSD and the Mind of the Universe (LSDMU)”*.

### Fixed
- Removed duplicate Fair Use blocks in generated HTML (builder now detects existing “Fair Use” headings).
- Removed the `sources.json` link from page headers.
- Eliminated the visible `ID: …` badge from topic headers.
- Standardized and simplified the **About this document** card to a single About line.

### Removed
- `sources.json` files from published `docs/educational/**` to avoid surfacing them on GitHub Pages.
- Pipeline-specific phrasing from provenance lines (RAG version strings).

### Provenance / Citation
- Unified citation across Markdown and HTML:
  *Cite as: **Bache Archive — Educational Docs Edition (2025)**. Based on the works of Christopher M. Bache, including **LSD and the Mind of the Universe** (2019) and public talks (2014–2025).*

---

## [2025-10-23 — Initial import]
- Initial migration of educational topic pages, quote packs, and repository scaffolding (README, LICENSE, LEGAL_NOTICE, .gitignore).
