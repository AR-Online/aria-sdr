from __future__ import annotations

# Thin wrapper so `python ingest_faqs.py` works from repo root.
# Delegates to scripts/ingest_faqs.py:main
from scripts.ingest_faqs import main

if __name__ == "__main__":
    main()
