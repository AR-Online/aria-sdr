# main.py
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import secrets
import time
from datetime import datetime, timezone
from typing import Any

import requests  # pyright: ignore[reportMissingModuleSource]
from dotenv import find_dotenv, load_dotenv  # pyright: ignore[reportMissingImports]
from fastapi import Body, Depends, FastAPI, HTTPException, Request, Header  # pyright: ignore[reportMissingImports]
from fastapi.responses import JSONResponse  # pyright: ignore[reportMissingImports]
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer  # pyright: ignore[reportMissingImports]
from pydantic import BaseModel
from requests.adapters import HTTPAdapter  # pyright: ignore[reportMissingModuleSource]
from urllib3.util.retry import Retry  # pyright: ignore[reportMissingImports]

# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# Boot / Config
# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# Load .env without overriding existing process env (CI-friendly)
load_dotenv(find_dotenv(), override=False)
DEBUG = (os.getenv("API_DEBUG", "false") or "").lower() == "true"
app = FastAPI(title="ARIA-SDR Endpoint", debug=DEBUG)

API_TOKEN = (os.getenv("FASTAPI_BEARER_TOKEN") or "").strip()
auth_scheme = HTTPBearer(auto_error=False)
log = logging.getLogger(__name__)

# Agno configuration
AGNO_ROUTING_WEBHOOK = os.getenv("AGNO_ROUTING_WEBHOOK", "https://agno.ar-infra.com.br/webhook/assist/routing")
AGNO_API_BASE_URL = os.getenv("AGNO_API_BASE_URL", "https://agno.ar-infra.com.br/api/v1")
AGNO_AUTH_TOKEN = os.getenv("AGNO_AUTH_TOKEN", "")
AGNO_BOT_ID = os.getenv("AGNO_BOT_ID", "")

# Cloudflare configuration
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
MINDCHAT_API_TOKEN = os.getenv("MINDCHAT_API_TOKEN", "")
MINDCHAT_API_BASE_URL = os.getenv("MINDCHAT_API_BASE_URL", "")
MINDCHAT_API_DOCS = os.getenv("MINDCHAT_API_DOCS", "")

# GitLab Webhook configuration
GITLAB_WEBHOOK_TOKEN = os.getenv("GITLAB_WEBHOOK_TOKEN", "dtransforma2026")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+5516997918658")


@app.exception_handler(Exception)
async def _unhandled_exc_handler(request: Request, exc: Exception):  # type: ignore[valid-type]
    try:
        import traceback

        with open("last_error.log", "w", encoding="utf-8") as f:
            f.write(f"path={request.url.path}\n")
            traceback.print_exc(file=f)
    except Exception:
        pass
    return JSONResponse(status_code=400, content={"detail": "unexpected_error"})


# Session para RAG com retry/backoff
_rag_session: requests.Session | None = None


def get_rag_session() -> requests.Session:
    global _rag_session
    if _rag_session is None:
        s = requests.Session()
        retries = Retry(
            total=2,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        _rag_session = s
    return _rag_session


def require_auth(cred: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> str:
    if not cred:
        raise HTTPException(401, "Missing Authorization header")
    token = (cred.credentials or "").strip()
    if token != API_TOKEN:
        raise HTTPException(401, "Invalid token")
    return token


# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# Models (uma vez sÃ³)
# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
class AssistRequest(BaseModel):
    input: str | None = None
    user_text: str | None = None
    # Compatibility with tests/clients that send {"message": "..."}
    message: str | None = None
    variables: dict[str, Any] | None = None
    channel: str | None = None
    thread_id: str | None = None
    metadata: dict[str, Any] | None = None


class AssistResponse(BaseModel):
    reply_text: str
    route: str | None = None
    thread_id: str | None = None
    variables: dict[str, Any] | None = None
    confidence: float | None = None
    next_action: str | None = None
    tags: list[str] | None = None
    # Optional flattened fields for clients
    volume_class: str | None = None
    volume_alto: bool | None = None
    fluxo_path: str | None = None
    trace_id: str | None = None
    tokens: dict[str, int] | None = None


# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# OpenAI (Assistants) â€” opcional
# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
ASSISTANT_TIMEOUT_SECONDS = float(os.getenv("ASSISTANT_TIMEOUT_SECONDS", "12"))
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")

try:
    from openai import OpenAI  # type: ignore

    client_assistant = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore
    client_assistant = None


def wait_run(thread_id: str, run_id: str, timeout_seconds: float | None = None):
    if client_assistant is None:
        return None
    deadline = time.time() + timeout_seconds if timeout_seconds and timeout_seconds > 0 else None
    while True:
        run = client_assistant.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status in ("completed", "failed", "cancelled", "expired", "requires_action"):
            return run
        if deadline and time.time() >= deadline:
            return None
        time.sleep(0.5)


def last_assistant_message(thread_id: str) -> str:
    if client_assistant is None:
        return ""
    msgs = client_assistant.beta.threads.messages.list(thread_id=thread_id)
    for m in msgs.data:
        if getattr(m, "role", "") == "assistant":
            try:
                return m.content[0].text.value
            except Exception:
                continue
    return ""


# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# Regras de negÃ³cio â€” triagem + volumetria
# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
def classify_route(
    user_text: str, v: dict[str, Any]
) -> tuple[str | None, dict[str, str], str | None]:
    t = (user_text or "").lower()
    route: str | None = None
    vars_out: dict[str, str] = {}
    next_action: str | None = None

    fp = str(v.get("fluxo_path") or "").strip().lower()
    if fp in {"envio", "recebimento"}:
        route = fp
    else:
        if any(
            k in t
            for k in ["recebi", "receb", "chegou", "abriu", "abertura", "confirmacao de leitura"]
        ):
            route = "recebimento"
        elif any(
            k in t for k in ["enviar", "envio", "mandar", "disparar", "disparo", "quero enviar"]
        ):
            route = "envio"

    if route == "envio":
        # Deterministic volumetry classification
        def classificar_volume(qtd: int) -> tuple[str, bool]:
            return ("alto", True) if qtd >= 1200 else ("baixo", False)

        vol_src = str(v.get("lead_volumetria", v.get("lead_duvida", ""))).lower()

        n: int | None = None
        m = re.findall(r"\d{1,3}(?:[\.,]\d{3})+|\d+", vol_src)
        if m:
            digits = re.sub(r"[^\d]", "", m[-1])
            if digits:
                n = int(digits)

        kw_high = re.search(
            r"(alto volume|grande volume|massivo|lote|mil|1k|1000\+|acima de|>\s*1000)", vol_src
        )

        if n is not None:
            vol_class, is_high = classificar_volume(n)
        else:
            is_high = bool(kw_high)
            vol_class = "alto" if is_high else "baixo"

        vars_out.update(
            {
                "volume_num": str(n or ""),
                "lead_volumetria": str(n or vol_src or ""),
                "volume_alto": "true" if is_high else "false",
                "volume_class": vol_class,
            }
        )
        next_action = "schedule" if is_high else "buy_credits"

    return route, vars_out, next_action


# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# RAG (Supabase + OpenAI) â€” endpoint interno
# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
SUPABASE_URL = (os.getenv("SUPABASE_URL", "") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "3072"))

HEADERS_JSON = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


class RagQueryIn(BaseModel):
    # Accept both "question" and legacy "query"
    question: str | None = None
    query: str | None = None
    # Accept both "k" and legacy "top_k"
    k: int | None = None
    top_k: int | None = None
    filter_source: str | None = None


class RagHit(BaseModel):
    content: str
    metadata: dict[str, Any] = {}
    similarity: float


class RagResponse(BaseModel):
    hits: list[RagHit]
    context: str


def _embed(q: str) -> list[float]:
    if OpenAI is None:
        raise RuntimeError("SDK OpenAI nÃ£o disponÃ­vel")
    client = OpenAI(api_key=OPENAI_API_KEY)
    vec = client.embeddings.create(model=EMBEDDING_MODEL, input=[q]).data[0].embedding
    if len(vec) != EMBEDDING_DIM:
        raise RuntimeError(f"Embedding dim {len(vec)} != {EMBEDDING_DIM}")
    return vec


def _rpc_match(
    query_emb: list[float],
    k: int,
    filter_source: str | None,
    session: requests.Session,
):
    url = f"{SUPABASE_URL}/rest/v1/rpc/match_aria_chunks"
    payload = {
        "query_embedding": query_emb,
        "match_count": int(k),
        "filter_source": filter_source,
    }
    r = session.post(url, headers=HEADERS_JSON, json=payload, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"RPC match failed: {r.status_code} -> {r.text}")
    return r.json()


@app.post("/rag/query", response_model=RagResponse)
def rag_query(q: RagQueryIn, session: requests.Session = Depends(get_rag_session)):
    question = (q.question or q.query or "").strip()
    k = int(q.k or q.top_k or 5)
    vec = _embed(question)
    rows = _rpc_match(vec, k, q.filter_source, session)
    hits = [
        RagHit(
            content=r.get("content", ""),
            metadata=r.get("metadata") or {},
            similarity=float(r.get("similarity", 0)),
        )
        for r in rows
    ]
    context = "\n\n".join(f"[{i+1}] {h.content}" for i, h in enumerate(hits))
    return RagResponse(hits=hits, context=context)


# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# HeurÃ­stica para acionar RAG + cliente interno
# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
KEYWORDS = ("como", "funciona", "preÃ§o", "prazo", "o que Ã©", "qual", "como faÃ§o")


def want_rag(text: str, v: dict[str, Any]) -> bool:
    if (v or {}).get("faq_mode") is True:
        return True
    t = (text or "").lower()
    return any(k in t for k in KEYWORDS)


RAG_ENABLE = os.getenv("RAG_ENABLE", "true").lower() == "true"
RAG_ENDPOINT = os.getenv("RAG_ENDPOINT", "http://127.0.0.1:8000/rag/query")
RAG_DEFAULT_SOURCE = os.getenv("RAG_DEFAULT_SOURCE", "faq")

# Optional alternative RAG backend: "rpc" (default via HTTP) or "pg" (direct Postgres hybrid)
RAG_BACKEND = os.getenv("RAG_BACKEND", "rpc").strip().lower()
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("PG_DSN")


def fetch_rag_context(
    question: str,
    k: int = 5,
    filter_source: str | None = RAG_DEFAULT_SOURCE,
    timeout: int = 12,
    session: requests.Session | None = None,
) -> str | None:
    payload = {"question": question, "k": int(k), "filter_source": filter_source}
    start = time.time()
    try:
        sess = session or get_rag_session()
        r = sess.post(RAG_ENDPOINT, json=payload, timeout=timeout)
        r.raise_for_status()
        data = r.json() or {}
        ctx = data.get("context") or None
        log.debug(
            "RAG context ok in %.2fs (k=%s, source=%s, size=%s)",
            time.time() - start,
            k,
            filter_source,
            len(ctx or ""),
        )
        return ctx
    except requests.Timeout:
        log.warning("RAG timeout after %ss", timeout)
        return None
    except Exception as e:
        log.warning("RAG offline/erro: %s", e)
        return None


def _pg_hybrid_search(question: str, k: int = 12) -> tuple[str | None, list[dict]]:
    """Optional direct-Postgres hybrid search (FTS + vector) using psycopg.

    Returns a tuple (context_text, refs). If unavailable or errors, returns (None, []).
    """
    if not DATABASE_URL:
        return None, []
    try:
        import psycopg  # type: ignore
    except Exception:
        log.debug("psycopg not installed; skipping PG hybrid search")
        return None, []

    # Embedding via OpenAI SDK if available
    try:
        if OpenAI is None or not OPENAI_API_KEY:
            return None, []
        client = OpenAI(api_key=OPENAI_API_KEY)
        emb = client.embeddings.create(model=EMBEDDING_MODEL, input=question).data[0].embedding
    except Exception as e:  # pragma: no cover
        log.warning("Embedding failed: %s", e)
        return None, []

    fts_rows: list[tuple] = []
    vec_rows: list[tuple] = []
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # FTS on content (Portuguese config); adjust to your schema
                cur.execute(
                    """
                    select id, document_id, heading, content,
                           0.0 as vscore,
                           ts_rank(to_tsvector('portuguese', content), websearch_to_tsquery('portuguese', %s)) as ts_score
                    from rag_chunks
                    where to_tsvector('portuguese', content) @@ websearch_to_tsquery('portuguese', %s)
                    order by ts_score desc
                    limit 50
                    """,
                    (question, question),
                )
                fts_rows = cur.fetchall() or []

                # Vector similarity (pgvector <=>). Assumes column name 'embedding'
                cur.execute(
                    """
                    select id, document_id, heading, content,
                           1 - (embedding <=> %s::vector) as vscore,
                           0.0 as ts_score
                    from rag_chunks
                    order by embedding <=> %s::vector
                    limit 50
                    """,
                    (emb, emb),
                )
                vec_rows = cur.fetchall() or []
    except Exception as e:
        log.warning("PG hybrid query failed: %s", e)
        return None, []

    # Simple Reciprocal Rank Fusion-like merge
    def rank_map(rows: list[tuple], key_index: int = 0) -> dict[Any, int]:
        return {row[key_index]: i for i, row in enumerate(rows)}

    r_fts = rank_map(fts_rows)
    r_vec = rank_map(vec_rows)
    combined: dict[Any, dict] = {}
    for rows in (fts_rows, vec_rows):
        for row in rows:
            _id, _doc, heading, content, vscore, ts_score = row
            if _id not in combined:
                combined[_id] = {
                    "heading": heading or "",
                    "content": content or "",
                    "vscore": float(vscore or 0.0),
                    "ts_score": float(ts_score or 0.0),
                    "source_title": str(_doc or ""),
                    "uri": None,
                }
    # Compute fusion score 1/(k + rank)
    for _id in combined.keys():
        rf = r_fts.get(_id, 10_000)
        rv = r_vec.get(_id, 10_000)
        combined[_id]["fusion"] = (1.0 / (60 + rf)) + (1.0 / (60 + rv))

    top_ids = sorted(combined.keys(), key=lambda i: combined[i]["fusion"], reverse=True)[: max(1, k)]
    items = [combined[i] for i in top_ids]

    context_text = ""
    refs: list[dict] = []
    for i, c in enumerate(items, 1):
        context_text += f"[{i}] {c['heading'] or ''}\n{c['content']}\n---\n"
        refs.append({
            "i": i,
            "title": c.get("source_title") or "",
            "uri": c.get("uri") or "",
        })

    return context_text or None, refs


def fetch_rag_bundle(question: str, k: int = 5) -> tuple[str | None, list[dict]]:
    """Unified RAG fetch that supports RPC or Postgres backends.

    Returns (context, refs). Refs non-empty only for PG backend.
    """
    if RAG_BACKEND == "pg":
        return _pg_hybrid_search(question, max(1, k))
    # default: RPC backend
    return fetch_rag_context(question, k), []

# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# Endpoint principal
# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”

@app.post("/webhook/assist/routing")
def agno_webhook_routing(
    request: Request,
    payload: dict = Body(default_factory=dict),
    _tok: str = Depends(require_auth),
):
    """Webhook do Agno - redireciona para o endpoint principal"""
    return assist_routing(request, payload, _tok)


@app.post("/webhook/assist/routing/debug")
def agno_webhook_routing_debug(
    request: Request,
    payload: dict = Body(default_factory=dict),
):
    """Webhook do Agno - versão debug sem autenticação"""
    log.info(f"Agno webhook debug received: {payload}")
    return {"status": "received", "payload": payload}
@app.post("/assist/routing")
def assist_routing(
    request: Request,
    payload: dict = Body(default_factory=dict),
    _tok: str = Depends(require_auth),
):
    t0 = time.time()
    try:
        with open("assist_debug.log", "a", encoding="utf-8") as _f:
            _f.write("enter\n")
    except Exception:
        pass
    # Accept multiple possible input fields
    user_text = str(
        (payload or {}).get("input")
        or (payload or {}).get("user_text")
        or (payload or {}).get("message")
        or ""
    ).strip()
    v_in: dict[str, Any] = dict((payload or {}).get("variables") or {})

    # 1) Regras determinÃ­sticas
    route, vars_out, next_action = classify_route(user_text, v_in)
    try:
        with open("assist_debug.log", "a", encoding="utf-8") as _f:
            _f.write("after_classify\n")
    except Exception:
        pass

    # 2) RAG opcional
    rag_ctx: str | None = None
    rag_refs: list[dict] = []
    need_rag = RAG_ENABLE and want_rag(user_text, v_in)
    if need_rag:
        rag_ctx, rag_refs = fetch_rag_bundle(user_text, k=5)
    try:
        with open("assist_debug.log", "a", encoding="utf-8") as _f:
            _f.write("after_rag\n")
    except Exception:
        pass

    if rag_ctx:
        vars_out["need_rag"] = "true"
        vars_out["rag_context"] = rag_ctx
        if rag_refs:
            vars_out["rag_refs"] = rag_refs

    # 3) Thread (se usar Assistant)
    # Precedence: header X-Thread-Id -> payload.thread_id -> fallback
    x_thread_id = (request.headers.get("x-thread-id") or "").strip()  # type: ignore[attr-defined]
    body_thread_id = str((payload or {}).get("thread_id") or "").strip()

    def ensure_thread_id(remetente: str, canal: str) -> str:
        base = f"{canal}:{remetente}".strip().lower()
        return "thrd_" + hashlib.sha256(base.encode()).hexdigest()[:24]

    app_thread_id = x_thread_id or body_thread_id
    if not app_thread_id:
        remetente = str(v_in.get("remetente") or "").strip()
        canal = str(v_in.get("canal") or "").strip()
        if remetente and canal:
            app_thread_id = ensure_thread_id(remetente, canal)
        else:
            app_thread_id = (
                f"thr_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(2)}"
            )
    assistant_thread_id: str | None = None
    if client_assistant is not None:
        try:
            assistant_thread_id = client_assistant.beta.threads.create().id
        except Exception:
            assistant_thread_id = None

    # 4) Assistant opcional
    reply_text = ""
    if client_assistant is not None and ASSISTANT_ID:
        try:
            system_rules = (
                "VocÃª Ã© a ARIA. Responda em pt-BR. "
                "Use APENAS o CONTEXTO quando fornecido; se faltar, diga que nÃ£o encontrou e ofereÃ§a encaminhar ao time."
            )
            prompt = (
                system_rules
                + (f"\n\nCONTEXTO:\n{rag_ctx}\n\n" if rag_ctx else "\n\n")
                + f"PERGUNTA:\n{user_text}"
            )
            th_id = assistant_thread_id or client_assistant.beta.threads.create().id
            client_assistant.beta.threads.messages.create(
                thread_id=th_id, role="user", content=prompt
            )
            run = client_assistant.beta.threads.runs.create(
                thread_id=th_id, assistant_id=ASSISTANT_ID
            )
            wait_run(th_id, run.id, ASSISTANT_TIMEOUT_SECONDS)
            reply_text = last_assistant_message(th_id)
            assistant_thread_id = th_id
        except Exception:
            reply_text = ""
    # If not using Assistants, attempt Chat Completions with RAG context
    if not reply_text and rag_ctx and OPENAI_API_KEY:
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            system_rules = (
                "Você é a ARIA, assistente da AR Online. Fale SEMPRE em pt-BR, tom cordial e objetivo. "
                "Siga LGPD: peça só o mínimo. Use APENAS as fontes fornecidas no CONTEXTO para responder. "
                "Quando faltar base, diga que vai encaminhar para o time responsável."
            )
            messages = [
                {"role": "system", "content": system_rules},
                {"role": "user", "content": f"PERGUNTA:\n{user_text}\n\nCONTEXTO:\n{rag_ctx}"},
            ]
            resp = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=messages,
                temperature=0.2,
            )
            reply_text = (resp.choices[0].message.content or "").strip()
        except Exception:
            reply_text = reply_text or ""
    try:
        with open("assist_debug.log", "a", encoding="utf-8") as _f:
            _f.write("after_assistant\n")
    except Exception:
        pass

    # 5) Fallback determinÃ­stico
    if not reply_text:
        if rag_ctx:
            reply_text = "Encontrei estes trechos relevantes e respondi com base neles."
            route = route or "faq"
        elif route == "recebimento":
            reply_text = (
                "Entendi que vocÃª recebeu uma notificaÃ§Ã£o. A AR Online Ã© o meio de envio; "
                "o conteÃºdo deve ser tratado diretamente com o remetente indicado na mensagem."
            )
        elif route == "envio":
            reply_text = "Certo! Informe uma estimativa do volume mensal (ex.: 50, 300, 1500) para sugerir o melhor caminho."
        else:
            reply_text = "Como posso te ajudar hoje?"
    try:
        with open("assist_debug.log", "a", encoding="utf-8") as _f:
            _f.write("after_fallback\n")
    except Exception:
        pass

    # Expose thread ids in variables and response
    vars_out["thread_id"] = app_thread_id
    if assistant_thread_id:
        vars_out["assistant_thread_id"] = assistant_thread_id
    # Structured JSON log for routing
    try:
        x_trace_id = (
            request.headers.get("x-trace-id") or request.headers.get("x-request-id") or ""
        ).strip()
        vol = str(
            vars_out.get("volume_num")
            or v_in.get("lead_volumetria")
            or v_in.get("lead_duvida")
            or ""
        )
        fluxo_path = str(v_in.get("fluxo_path") or "").strip()
        dur_ms = int((time.time() - t0) * 1000)
        log.info(
            json.dumps(
                {
                    "level": "INFO",
                    "event": "routing",
                    "thread_id": app_thread_id,
                    "trace_id": x_trace_id,
                    "volume": vol,
                    "fluxo_path": fluxo_path,
                    "dur_ms": dur_ms,
                },
                ensure_ascii=False,
            )
        )
    except Exception:
        pass
    try:
        with open("assist_debug.log", "a", encoding="utf-8") as _f:
            _f.write("before_return\n")
    except Exception:
        pass

    # Append Fontes section if we have refs
    try:
        if rag_ctx and rag_refs:
            tops = rag_refs[:5]
            fontes = "\n".join(f"- {r.get('title','')} ({r.get('uri','')})" for r in tops)
            if fontes.strip():
                reply_text = reply_text.rstrip() + "\n\nFontes:\n" + fontes
    except Exception:
        pass

    # Flattened fields derived from variables/context
    _vol_class: str | None = None
    _vol_alto_bool: bool | None = None
    try:
        if isinstance(vars_out, dict):
            _vc = vars_out.get("volume_class")
            _va = vars_out.get("volume_alto")
            _vol_class = str(_vc) if _vc is not None else None
            if isinstance(_va, bool):
                _vol_alto_bool = _va
            elif isinstance(_va, str):
                _vol_alto_bool = _va.strip().lower() == "true"
    except Exception:
        _vol_class = _vol_class or None
        _vol_alto_bool = _vol_alto_bool or None

    return AssistResponse(
        reply_text=reply_text,
        route=route,
        thread_id=app_thread_id,
        variables=vars_out or None,
        confidence=0.75 if route else None,
        next_action=next_action,
        tags=[],
        volume_class=_vol_class,
        volume_alto=_vol_alto_bool,
        fluxo_path=fluxo_path if "fluxo_path" in locals() and fluxo_path else None,
        trace_id=x_trace_id if "x_trace_id" in locals() and x_trace_id else None,
        tokens=None,
    )


@app.post("/webhookassistrouting")
def webhook_assist_routing(
    request: Request,
    payload: dict = Body(default_factory=dict),
    _tok: str = Depends(require_auth),
):
    # Simple alias to the main routing endpoint for compatibility
    return assist_routing(request=request, payload=payload, _tok=_tok)


# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# Health
# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
@app.get("/cloudflare/metrics")
def cloudflare_metrics(_tok: str = Depends(require_auth)):
    """Obtém métricas do Cloudflare para ARIA-SDR"""
    try:
        from cloudflare_client import get_cloudflare_metrics
        return get_cloudflare_metrics()
    except ImportError:
        return {"success": False, "error": "Módulo Cloudflare não disponível"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/cloudflare/setup")
def cloudflare_setup(_tok: str = Depends(require_auth)):
    """Configura proteção Cloudflare para ARIA-SDR"""
    try:
        from cloudflare_client import setup_cloudflare_protection
        return setup_cloudflare_protection()
    except ImportError:
        return {"success": False, "error": "Módulo Cloudflare não disponível"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/cloudflare/purge-cache")
def cloudflare_purge_cache(
    urls: list[str] = Body(default_factory=list),
    _tok: str = Depends(require_auth)
):
    """Limpa cache do Cloudflare"""
    try:
        from cloudflare_client import CloudflareAPI
        
        cf = CloudflareAPI()
        zone_id = cf.get_zone_id("api.ar-online.com.br")
        
        if not zone_id:
            return {"success": False, "error": "Zone ID não encontrado"}
        
        result = cf.purge_cache(zone_id, urls if urls else None)
        return result
        
    except ImportError:
        return {"success": False, "error": "Módulo Cloudflare não disponível"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# WhatsApp Integration via Mindchat
# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”

@app.post("/whatsapp/webhook")
def whatsapp_webhook(
    request: Request,
    payload: dict = Body(default_factory=dict),
    _tok: str = Depends(require_auth)
):
    """Webhook para receber mensagens do WhatsApp via Mindchat"""
    
    try:
        # Extrair dados da mensagem
        message_data = {
            "from": payload.get("from", ""),
            "to": payload.get("to", ""),
            "message": payload.get("message", ""),
            "timestamp": payload.get("timestamp", ""),
            "message_id": payload.get("id", ""),
            "type": payload.get("type", "text")
        }
        
        log.info(f"WhatsApp message received: {message_data}")
        
        # Processar com ARIA
        response = process_aria_message(message_data)
        
        # Enviar resposta via Mindchat
        send_whatsapp_response(response, message_data["from"])
        
        return {"status": "processed", "message_id": message_data["message_id"]}
        
    except Exception as e:
        log.error(f"Erro no webhook WhatsApp: {e}")
        return {"status": "error", "error": str(e)}


def process_aria_message(message_data: dict) -> dict:
    """Processa mensagem usando lógica da ARIA"""
    
    try:
        # Usar o mesmo endpoint de routing
        routing_payload = {
            "channel": "whatsapp",
            "sender": message_data["from"],
            "user_text": message_data["message"],
            "thread_id": f"wa_{message_data['from']}_{int(time.time())}"
        }
        
        # Chamar endpoint interno
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.post(
            "/assist/routing",
            json=routing_payload,
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        
        return response.json()
        
    except Exception as e:
        log.error(f"Erro ao processar mensagem ARIA: {e}")
        return {"reply_text": "Desculpe, ocorreu um erro ao processar sua mensagem."}


def send_whatsapp_response(response: dict, to_number: str):
    """Envia resposta via Mindchat WhatsApp API"""
    
    try:
        mindchat_payload = {
            "to": to_number,
            "message": response.get("reply_text", "Desculpe, não entendi sua mensagem."),
            "type": "text"
        }
        
        headers = {
            "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(  # pyright: ignore[reportAssignmentType]
            f"{MINDCHAT_API_BASE_URL}/api/whatsapp/send",
            json=mindchat_payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            log.info(f"Resposta WhatsApp enviada para {to_number}")
        else:
            log.error(f"Erro ao enviar WhatsApp: {response.status_code} - {response.text}")
            
    except Exception as e:
        log.error(f"Erro ao enviar WhatsApp: {e}")


@app.get("/whatsapp/status")
def whatsapp_status(_tok: str = Depends(require_auth)):
    """Status da integração WhatsApp"""
    
    try:
        # Verificar conexão com Mindchat
        headers = {
            "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{MINDCHAT_API_BASE_URL}/api/whatsapp/status",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            mindchat_status = response.json()
            return {
                "status": "connected",
                "mindchat_status": mindchat_status,
                "aria_status": "active",
                "webhook_url": f"{API_HOST}:{API_PORT}/whatsapp/webhook"  # pyright: ignore[reportUndefinedVariable]
            }
        else:
            return {
                "status": "error",
                "error": f"Mindchat API error: {response.status_code}",
                "aria_status": "active"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "aria_status": "active"
        }


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/auth_debug")
def auth_debug(_tok: str = Depends(require_auth)):
    return {"tok": _tok}


import logging
import os
from collections.abc import Mapping

from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

try:
    from fastapi import HTTPException, Request, status  # type: ignore
except Exception:  # pragma: no cover
    Request = None  # type: ignore
    HTTPException = Exception  # type: ignore


# Ensure .env is loaded, but do not override already-set env vars
load_dotenv(override=False)

# Basic logging; no-op if already configured elsewhere
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
logger = logging.getLogger(__name__)


def get_bearer_from_headers(headers: Mapping[str, str]) -> str | None:
    auth = headers.get("authorization") or headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        return None
    return auth.split(" ", 1)[1].strip()


def require_bearer(request: Request) -> None:  # type: ignore[valid-type]
    """FastAPI dependency to enforce Bearer token, if FastAPI is present.

    This is a no-op outside FastAPI contexts.
    """
    if Request is None:  # FastAPI not available
        return
    token = get_bearer_from_headers(request.headers)  # type: ignore[arg-type]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")  # type: ignore[arg-type]
    # Prefer FASTAPI_BEARER_TOKEN; allow legacy BEARER_TOKEN as a fallback, but never default to a hardcoded value
    expected = (os.getenv("FASTAPI_BEARER_TOKEN") or os.getenv("BEARER_TOKEN") or "").strip()
    if not expected:
        # Auth is enabled but the server is not configured with a token
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing server token config")  # type: ignore[arg-type]
    if token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")  # type: ignore[arg-type]


# GitLab Webhook Functions
def validate_gitlab_webhook_token(authorization: str = Header(None)) -> bool:
    """Valida o token de autorização do webhook GitLab"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    expected_token = f"Bearer {GITLAB_WEBHOOK_TOKEN}"
    if authorization != expected_token:
        raise HTTPException(status_code=401, detail="Invalid authorization token")
    
    return True

async def send_whatsapp_notification(message: str, event_type: str = "gitlab_webhook") -> dict[str, Any]:
    """Envia notificação via WhatsApp usando Mindchat API"""
    try:
        whatsapp_data = {
            "to": WHATSAPP_NUMBER,
            "message": f"🤖 ARIA Notification ({event_type}):\n{message}",
            "source": "gitlab_webhook",
            "timestamp": datetime.now().isoformat()
        }
        
        headers = {
            "Authorization": f"Bearer {MINDCHAT_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{MINDCHAT_API_BASE_URL}/webhook/whatsapp",
            json=whatsapp_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            log.info(f"Notificação WhatsApp enviada: {message}")
            return {"status": "success", "response": response.json()}
        else:
            log.error(f"Erro ao enviar WhatsApp: {response.status_code} - {response.text}")
            return {"status": "error", "error": response.text}
            
    except Exception as e:
        log.error(f"Erro ao enviar notificação WhatsApp: {e}")
        return {"status": "error", "error": str(e)}

# GitLab Webhook Endpoints
@app.post("/webhook/gitlab/aria")
async def gitlab_webhook_endpoint(
    request: Request,
    payload: dict[str, Any] = Body(...),
    _: bool = Depends(validate_gitlab_webhook_token)
) -> JSONResponse:
    """Endpoint principal para receber webhooks do GitLab"""
    
    log.info(f"Webhook GitLab recebido: {payload.get('aria_action', 'unknown')}")
    
    try:
        # Processar evento baseado no tipo
        event_type = payload.get("aria_action", "unknown")
        project_name = payload.get("project_name", "projeto desconhecido")
        
        if event_type == "pipeline_notification":
            pipeline_status = payload.get("pipeline_status", "unknown")
            commit_message = payload.get("commit_message", "Sem mensagem")
            branch = payload.get("branch", "branch desconhecida")
            
            if pipeline_status == "success":
                message = f"✅ Pipeline do {project_name} executado com sucesso!\n📝 Commit: {commit_message}\n🌿 Branch: {branch}"
            elif pipeline_status == "failed":
                message = f"❌ Pipeline do {project_name} falhou!\n📝 Commit: {commit_message}\n🌿 Branch: {branch}"
            else:
                message = f"🔄 Pipeline do {project_name} - Status: {pipeline_status}\n📝 Commit: {commit_message}\n🌿 Branch: {branch}"
            
            whatsapp_result = await send_whatsapp_notification(message, "pipeline")
            
        elif event_type == "deployment_notification":
            environment = payload.get("environment", "ambiente desconhecido")
            deployment_status = payload.get("deployment_status", "unknown")
            commit_message = payload.get("commit_message", "Sem mensagem")
            
            if deployment_status == "success":
                message = f"🚀 Deploy do {project_name} para {environment} concluído!\n📝 Commit: {commit_message}"
            elif deployment_status == "failed":
                message = f"💥 Deploy do {project_name} para {environment} falhou!\n📝 Commit: {commit_message}"
            else:
                message = f"⏳ Deploy do {project_name} para {environment} - Status: {deployment_status}\n📝 Commit: {commit_message}"
            
            whatsapp_result = await send_whatsapp_notification(message, "deployment")
            
        elif event_type == "merge_request_notification":
            mr_title = payload.get("merge_request_title", "Sem título")
            mr_state = payload.get("merge_request_state", "unknown")
            author_name = payload.get("author_name", "Autor desconhecido")
            
            if mr_state == "opened":
                message = f"📝 Nova MR no {project_name}:\n📋 Título: {mr_title}\n👤 Autor: {author_name}"
            elif mr_state == "merged":
                message = f"✅ MR mergeada no {project_name}:\n📋 Título: {mr_title}\n👤 Autor: {author_name}"
            elif mr_state == "closed":
                message = f"❌ MR fechada no {project_name}:\n📋 Título: {mr_title}\n👤 Autor: {author_name}"
            else:
                message = f"🔄 MR atualizada no {project_name}:\n📋 Título: {mr_title}\n👤 Autor: {author_name}\n📊 Status: {mr_state}"
            
            whatsapp_result = await send_whatsapp_notification(message, "merge_request")
            
        elif event_type == "push_notification":
            commit_message = payload.get("commit_message", "Sem mensagem")
            branch = payload.get("branch", "branch desconhecida")
            commit_count = payload.get("commit_count", "1")
            user_name = payload.get("user_name", "Usuário desconhecido")
            
            message = f"📤 Push no {project_name}:\n🌿 Branch: {branch}\n📝 Commit: {commit_message}\n📊 Commits: {commit_count}\n👤 Autor: {user_name}"
            
            whatsapp_result = await send_whatsapp_notification(message, "push")
            
        else:
            log.warning(f"Tipo de evento não reconhecido: {event_type}")
            return JSONResponse(
                content={
                    "status": "ignored",
                    "message": f"Evento {event_type} ignorado",
                    "processed_at": datetime.now().isoformat(),
                    "event_type": event_type
                }
            )
        
        log.info(f"Webhook processado com sucesso: {event_type}")
        return JSONResponse(
            content={
                "status": "processed",
                "message": f"Evento {event_type} processado",
                "processed_at": datetime.now().isoformat(),
                "event_type": event_type,
                "whatsapp_result": whatsapp_result
            }
        )
        
    except Exception as e:
        log.error(f"Erro ao processar webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/webhook/gitlab/health")
async def gitlab_webhook_health() -> JSONResponse:
    """Health check para o webhook GitLab"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "ARIA GitLab Webhook",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.post("/webhook/gitlab/test")
async def test_gitlab_webhook(
    test_payload: dict[str, Any] = Body(...),
    _: bool = Depends(validate_gitlab_webhook_token)
) -> JSONResponse:
    """Endpoint para testar webhook GitLab"""
    
    log.info("Teste de webhook GitLab iniciado")
    
    # Adicionar dados de teste se não fornecidos
    if "aria_action" not in test_payload:
        test_payload["aria_action"] = "pipeline_notification"
    if "project_name" not in test_payload:
        test_payload["project_name"] = "aria-sdr-test"
    if "pipeline_status" not in test_payload:
        test_payload["pipeline_status"] = "success"
    
    # Processar como webhook normal
    return await gitlab_webhook_endpoint(None, test_payload, True)
