#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob
fail=0
for f in docs/educational/*/index.md; do
  if ! grep -q '^openalex_author:' "$f"; then
    echo "✗ missing openalex_author → $f"; fail=1
  else
    echo "✓ $f"
  fi
done
exit $fail
