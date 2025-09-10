import importlib
import os
import re

from fastapi.testclient import TestClient


def make_client() -> TestClient:
    # Ensure app boots without external services
    # main.py uses load_dotenv(override=True), so align with .env default
    os.environ["FASTAPI_BEARER_TOKEN"] = "realizati"
    os.environ["OPENAI_API_KEY"] = ""  # disable OpenAI client
    os.environ["RAG_ENABLE"] = "false"  # avoid RAG calls

    # Import (or reload) app after env is set so globals pick up values
    import main  # noqa

    importlib.reload(main)
    return TestClient(main.app)


def _auth_headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    base = {"Authorization": "Bearer realizati"}
    if extra:
        base.update(extra)
    return base


def test_thread_id_header_wins() -> None:
    client = make_client()
    headers = _auth_headers({"X-Thread-Id": "hdr_999"})
    payload = {"message": "hello", "thread_id": "body_123"}
    resp = client.post("/assist/routing", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["thread_id"] == "hdr_999"
    assert data.get("variables", {}).get("thread_id") == "hdr_999"


def test_thread_id_body_fallback() -> None:
    client = make_client()
    headers = _auth_headers()
    payload = {"message": "hello", "thread_id": "body_123"}
    resp = client.post("/assist/routing", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["thread_id"] == "body_123"


def test_thread_id_generated_when_missing() -> None:
    client = make_client()
    headers = _auth_headers()
    payload = {"message": "hello"}
    resp = client.post("/assist/routing", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    tid = data["thread_id"]
    assert isinstance(tid, str) and tid
    assert tid.startswith("thr_")
    # Ensure matches pattern thr_YYYYMMDDHHMMSS_xx (hex)
    assert re.match(r"^thr_\d{14}_[0-9a-f]{4}$", tid), tid
