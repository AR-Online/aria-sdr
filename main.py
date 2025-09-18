# main.py
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import secrets
import time
from datetime import UTC, datetime
from typing import Any

import requests
from dotenv import find_dotenv, load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# Boot / Config
# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# Load .env without overriding existing process env (CI-friendly)
load_dotenv(find_dotenv(), override=False)
DEBUG = (os.getenv("API_DEBUG", "false") or "").lower() == "true"
app = FastAPI(title="ARIA Endpoint", debug=DEBUG)

API_TOKEN = (os.getenv("FASTAPI_BEARER_TOKEN") or "").strip()
auth_scheme = HTTPBearer(auto_error=False)
log = logging.getLogger(__name__)


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


# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# Endpoint principal
# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
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
    need_rag = RAG_ENABLE and want_rag(user_text, v_in)
    if need_rag:
        rag_ctx = fetch_rag_context(user_text)
    try:
        with open("assist_debug.log", "a", encoding="utf-8") as _f:
            _f.write("after_rag\n")
    except Exception:
        pass

    if rag_ctx:
        vars_out["need_rag"] = "true"
        vars_out["rag_context"] = rag_ctx

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
                f"thr_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(2)}"
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


# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
# Health
# â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”â€”
@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/auth_debug")
def auth_debug(_tok: str = Depends(require_auth)):
    return {"tok": _tok}


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
    # Prefer FASTAPI_BEARER_TOKEN; allow legacy BEARER_TOKEN as a fallback, but never default to a hardcoded value
    expected = (os.getenv("FASTAPI_BEARER_TOKEN") or os.getenv("BEARER_TOKEN") or "").strip()
    if not expected:
        # Auth is enabled but the server is not configured with a token
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing server token config")  # type: ignore[arg-type]
    if token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")  # type: ignore[arg-type]
