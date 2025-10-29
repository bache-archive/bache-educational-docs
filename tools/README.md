# Educational Docs Tooling

This folder contains the 3-step pipeline used to **(1) harvest**, **(2) merge**, and **(3) build** topic pages under `docs/educational/<topic-id>/`.

- **This repo:** `bache-educational-docs` (public). Holds educational topic pages and harvested quote packs.
- **Upstream archive:** `chris-bache-archive` (separate repo). Transcripts-only (CC0) after the split; educational materials live **here**, not there.
- **Retrieval backends (you run these locally):**
  - **Talks RAG** → `bache-rag-api` on **http://127.0.0.1:8000**
  - **Book RAG** → `lsdmu-rag-api` on **http://127.0.0.1:9000**

Educational pages are produced **book-first**: we pull top book passages, then add corroborating talk quotes (with timestamps).

---

## Folder structure

bache-educational-docs/
├── docs/
│   └── educational/
│       └── /
│           ├── index.md         # rebuilt Markdown page
│           ├── index.html       # rebuilt HTML page
│           └── sources.json     # merged citations driving the build
└── reports/
└── quote_packs/
└── /
└── /
├── book.search.json    # harvested from book RAG (:9000)
└── talks.search.json   # harvested from talks RAG (:8000)

---

## Prereqs & environment

Both RAG servers are FastAPI apps exposing a `POST /search` endpoint. They may rely on `OPENAI_API_KEY` and local FAISS/Parquet files.

**Run them in separate terminals:**

**Talks RAG (port 8000)**
```bash
export OPENAI_API_KEY=<your key>
export FAISS_INDEX_PATH=vectors/bache-talks.index.faiss
export METADATA_PATH=vectors/bache-talks.embeddings.parquet
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Book RAG (port 9000)

export OPENAI_API_KEY=<your key>
export FAISS_INDEX_PATH=vectors/lsdmu-book.index.faiss
export METADATA_PATH=vectors/lsdmu-book.embeddings.parquet
export EMBED_MODEL=text-embedding-3-large
export EMBED_DIM=3072
uvicorn app:app --host 0.0.0.0 --port 9000 --reload

Health checks (expect at least something back):

Some FastAPI apps don’t define /health. Seeing {"detail":"Not Found"} is fine; just verify /search responds (usually 405 on GET, 200 on POST).

# Talks RAG
curl -sS http://127.0.0.1:8000/           || true
curl -sS -X POST http://127.0.0.1:8000/search -H 'Content-Type: application/json' -d '{"q":"test","k":1}' || true

# Book RAG
curl -sS http://127.0.0.1:9000/           || true
curl -sS -X POST http://127.0.0.1:9000/search -H 'Content-Type: application/json' -d '{"q":"test","k":1}' || true

If /search returns JSON results (or at least a structured response), you’re good.

⸻

The three tools

1) harvest_quote_packs.py

Queries both RAGs and writes raw results into quote packs.

Common flags
	•	--topics Comma-separated list of topic IDs (match directory names in docs/educational/)
	•	--book-endpoint (default you supply): http://127.0.0.1:9000/search
	•	--talks-endpoint: http://127.0.0.1:8000/search
	•	--max-book, --max-talks, --max-per-talk caps
	•	--out output directory (usually reports/quote_packs/<YYYY-MM-DD>)

Output per topic

reports/quote_packs/<DATE>/<topic-id>/book.search.json
reports/quote_packs/<DATE>/<topic-id>/talks.search.json

Result shape (typical, flexible):

[
  {
    "text": "…passage…",
    "source_id": "lsdmu ch.9 §4 ¶1",     // book ref OR a talk id
    "score": 0.82,
    "meta": {
      "chapter": 9, "section": 4, "paragraph": 1,
      "ts_url": "https://youtu.be/…?t=2815",     // for talks
      "start_sec": 2815
    }
  }
]


⸻

2) merge_harvest_into_sources.py

Combines the day’s book.search.json + talks.search.json into a single sources.json for a topic, enforcing book-first ordering and de-duping.

Flags
	•	--quote-packs reports/quote_packs/<DATE>
	•	--topic-id <topic>
	•	--sources docs/educational/<topic>/sources.json
	•	--overwrite to replace in place

Output structure (simplified):

{
  "book_citations": [ { "text": "...", "ref": "lsdmu ch.9 §4 ¶1", ... } ],
  "talk_citations": [ { "text": "...", "ts_url": "https://...", ... } ]
}

You can hand-prune weak quotes in sources.json before building.

⸻

3) build_educational_docs_full.py

Generates index.md and index.html from sources.json using a standard page template:

Frontmatter
	•	title, id, date, version, source_policy, status, editor

Sections
	1.	Curated weave (book-first synthesis)
	2.	Primary citations (book — verbatim excerpts)
	3.	Supporting transcript quotes (verbatim with timestamps)
	4.	Notes & synthesis (optional)
	5.	Provenance
	6.	Fair Use Notice

Useful flags
	•	--root docs/educational
	•	--topic-id <topic>
	•	--stylesheet /assets/style.css (optional absolute)
	•	--site-base /bache-educational-docs (for absolute links if needed)

⸻

Quick smoke test (single topic)

From repo root:

# 0) choose a fresh run dir
RUN_DATE=$(date +%F)
OUT="reports/quote_packs/$RUN_DATE"
mkdir -p "$OUT"

# 1) harvest (talks :8000, book :9000)
python3 tools/harvest_quote_packs.py \
  --topics future-human \
  --talks-endpoint http://127.0.0.1:8000/search \
  --book-endpoint  http://127.0.0.1:9000/search \
  --max-talks 50 --max-book 25 --max-per-talk 2 \
  --out "$OUT"

# you should now have:
# reports/quote_packs/$RUN_DATE/future-human/{book.search.json,talks.search.json}

# 2) merge into sources.json
python3 tools/merge_harvest_into_sources.py \
  --quote-packs "$OUT" \
  --topic-id future-human \
  --sources docs/educational/future-human/sources.json \
  --overwrite

# 3) build pages
python3 tools/build_educational_docs_full.py \
  --root docs/educational \
  --topic-id future-human \
  --stylesheet /assets/style.css \
  --site-base /bache-educational-docs

# publish
git add "reports/quote_packs/$RUN_DATE/future-human" \
        docs/educational/future-human/index.*
git commit -m "harvest/merge/build: future-human refresh ($RUN_DATE)"
git push origin main


⸻

Troubleshooting
	•	curl -sS localhost:8000/health returns 404
Not all apps define /health. Try:
	•	curl -sS http://127.0.0.1:8000/ (HTML/JSON welcome)
	•	curl -sS -X POST http://127.0.0.1:8000/search -H 'Content-Type: application/json' -d '{"q":"test","k":1}'
	•	Connection refused on :9000 or :8000
Make sure each server is actually running on the expected port and not blocked by a firewall. Use lsof -nP -iTCP:8000 -sTCP:LISTEN to check.
	•	No timestamps in talk quotes
Ensure the talks RAG metadata includes start_sec/ts_url. The merger/builders will pass them through if present.
	•	Styling
Use --stylesheet /assets/style.css to link a shared CSS (served from the repo root in GitHub Pages).

⸻

Relationship to chris-bache-archive
	•	chris-bache-archive = transcripts-only (CC0) corpus and supporting assets; no educational/book excerpts remain in its history after the split.
	•	bache-educational-docs (this repo) = fair-use educational commentary that quotes LSD and the Mind of the Universe and cites public talks with timestamps. Different license and purpose by design.

