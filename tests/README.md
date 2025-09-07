Smoke tests for the API endpoints

How to run

- Ensure the API is running locally and reachable (default http://localhost:8000).
- Optionally set environment variables:
  - BASE_URL: Base URL of the API (e.g., http://localhost:8000)
  - BEARER_TOKEN: Token for Authorization header (default: realizati)
- Install dev deps (if needed): pip install pytest requests
- Run: pytest -q tests/test_smoke_api.py
