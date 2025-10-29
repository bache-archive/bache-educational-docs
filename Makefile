# ---------------------------------------------------------------------
# Generate SHA256 checksums for public release (HTML + Markdown only)
# Usage: make checksums VERSION=v1.0.0
# ---------------------------------------------------------------------

VERSION ?= v1.0.0

checksums:
	@mkdir -p checksums
	@echo "🔍 Generating SHA256 checksums for $(VERSION)..."
	@if command -v sha256sum >/dev/null 2>&1; then \
	  find README.md LICENSE.md LEGAL_NOTICE.md CHANGELOG.md \
	       index.html sitemap.xml robots.txt googleb87f06a4d8a4ae9e.html \
	       assets docs/educational -type f \
	       ! -name "*.bak.*" ! -name ".DS_Store" \
	       -exec sha256sum {} \; | sort > checksums/sha256sum_$(VERSION).txt; \
	else \
	  find README.md LICENSE.md LEGAL_NOTICE.md CHANGELOG.md \
	       index.html sitemap.xml robots.txt googleb87f06a4d8a4ae9e.html \
	       assets docs/educational -type f \
	       ! -name "*.bak.*" ! -name ".DS_Store" \
	       -exec shasum -a 256 {} \; | sort > checksums/sha256sum_$(VERSION).txt; \
	fi
	@echo "✅ checksums/sha256sum_$(VERSION).txt created."
