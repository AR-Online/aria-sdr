Smoke tests for the API endpoints

How to run

- Ensure the API is running locally and reachable (default <http://127.0.0.1:8000>).
- Optionally set environment variables:
  - `BASE_URL`: Base URL of the API (defaults to `http://127.0.0.1:8000`)
  - `BEARER_TOKEN`: Token for Authorization header (no default in app; tests use your env value)
- Install dev deps (if needed): `pip install pytest requests`
- Run: `pytest -q tests/test_smoke_api.py`

Notes
- On Windows, prefer `127.0.0.1` over `localhost` to avoid intermittent connection resets.
