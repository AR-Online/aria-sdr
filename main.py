# main.py
from __future__ import annotations

import logging
import os
import re
import secrets
import time
from typing import Any
import json
from datetime import datetime

import requests
from dotenv import find_dotenv, load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ——————————————————————————————————————————————————
# Boot / Config
# ——————————————————————————————————————————————————
# Load .env without overriding existing process env (CI-friendly)
load_dotenv(find_dotenv(), override=False)
app = FastAPI(title="ARIA Endpoint")

API_TOKEN = (os.getenv("FASTAPI_BEARER_TOKEN") or "").strip()
auth_scheme = HTTPBearer(auto_error=False)
log = logging.getLogger(__name__)

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
        raise HTTPException(401, "Token inválido")
    return token


# ——————————————————————————————————————————————————
# Models (uma vez só)
# ——————————————————————————————————————————————————
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


# ——————————————————————————————————————————————————
# OpenAI (Assistants) — opcional
# ——————————————————————————————————————————————————
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
ASSISTANT_TIMEOUT_SECONDS = float(os.getenv("ASSISTANT_TIMEOUT_SECONDS", "12"))

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


# ——————————————————————————————————————————————————
# Regras de negócio — triagem + volumetria
# ——————————————————————————————————————————————————
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
        limiar = int(v.get("VOLUME_ALTO_LIMIAR", 1200))
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
        is_high = (n is not None and n >= limiar) or bool(kw_high)

        vars_out.update(
            {
                "volume_num": str(n or ""),
                "volume_alto": "true" if is_high else "false",
                "volume_class": "alto" if is_high else "baixo",
            }
        )
        next_action = "schedule" if is_high else "buy_credits"

    return route, vars_out, next_action


# ——————————————————————————————————————————————————
# RAG (Supabase + OpenAI) — endpoint interno
# ——————————————————————————————————————————————————
SUPABASE_URL = (os.getenv("SUPABASE_URL", "") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))

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
        raise RuntimeError("SDK OpenAI não disponível")
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


# ——————————————————————————————————————————————————
# Heurística para acionar RAG + cliente interno
# ——————————————————————————————————————————————————
KEYWORDS = ("como", "funciona", "preço", "prazo", "o que é", "qual", "como faço")


def want_rag(text: str, v: dict[str, Any]) -> bool:
    if (v or {}).get("faq_mode") is True:
        return True
    t = (text or "").lower()
    return any(k in t for k in KEYWORDS)


RAG_ENABLE = os.getenv("RAG_ENABLE", "true").lower() == "true"
RAG_ENDPOINT = os.getenv("RAG_ENDPOINT", "http://127.0.0.1:8000/rag/query")
RAG_DEFAULT_SOURCE = os.getenv("RAG_DEFAULT_SOURCE", "faq")


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


# ——————————————————————————————————————————————————
# Endpoint principal
# ——————————————————————————————————————————————————
@app.post("/assist/routing", response_model=AssistResponse)
def assist_routing(
    req: AssistRequest,
    request: Request,
    _tok: str = Depends(require_auth),
    session: requests.Session = Depends(get_rag_session),
):
    t0 = time.time()
    # Accept multiple possible input fields
    user_text = (req.input or req.user_text or req.message or "").strip()
    v_in: dict[str, Any] = dict(req.variables or {})

    # 1) Regras determinísticas
    route, vars_out, next_action = classify_route(user_text, v_in)

    # 2) RAG opcional
    rag_ctx: str | None = None
    need_rag = RAG_ENABLE and want_rag(user_text, v_in)
    if need_rag:
        rag_ctx = fetch_rag_context(user_text, session=session)
        if rag_ctx:
            vars_out["need_rag"] = "true"
            vars_out["rag_context"] = rag_ctx

    # 3) Thread (se usar Assistant)
    # Precedence: header X-Thread-Id -> payload.thread_id -> fallback
    x_thread_id = (request.headers.get("x-thread-id") or "").strip()  # type: ignore[attr-defined]
    app_thread_id = (
        x_thread_id
        or (req.thread_id or "").strip()
        or f"thr_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(2)}"
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
                "Você é a ARIA. Responda em pt-BR. "
                "Use APENAS o CONTEXTO quando fornecido; se faltar, diga que não encontrou e ofereça encaminhar ao time."
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

    # 5) Fallback determinístico
    if not reply_text:
        if rag_ctx:
            reply_text = "Encontrei estes trechos relevantes e respondi com base neles."
            route = route or "faq"
        elif route == "recebimento":
            reply_text = (
                "Entendi que você recebeu uma notificação. A AR Online é o meio de envio; "
                "o conteúdo deve ser tratado diretamente com o remetente indicado na mensagem."
            )
        elif route == "envio":
            reply_text = "Certo! Informe uma estimativa do volume mensal (ex.: 50, 300, 1500) para sugerir o melhor caminho."
        else:
            reply_text = "Como posso te ajudar hoje?"

    # Expose thread ids in variables and response
    vars_out["thread_id"] = app_thread_id
    if assistant_thread_id:
        vars_out["assistant_thread_id"] = assistant_thread_id
    # Structured JSON log for routing
    try:
        x_trace_id = (
            (request.headers.get("x-trace-id") or request.headers.get("x-request-id") or "")
            .strip()
        )
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

    return AssistResponse(
        reply_text=reply_text,
        route=route,
        thread_id=app_thread_id,
        variables=vars_out or None,
        confidence=0.75 if route else None,
        next_action=next_action,
        tags=[],
    )


# ——————————————————————————————————————————————————
# Health
# ——————————————————————————————————————————————————
@app.get("/healthz")
def healthz():
    return {"ok": True}


import logging
import os
from collections.abc import Mapping

from dotenv import load_dotenv

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
    expected = os.getenv("BEARER_TOKEN", "realizati")
    if token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")  # type: ignore[arg-type]
