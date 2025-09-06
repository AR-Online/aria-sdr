import os
import re
import time
import secrets
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
from typing import Any, Dict, Optional, Tuple, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv

# ---------------------------------------------------------------------------
# Config / Credenciais
# ---------------------------------------------------------------------------
load_dotenv(find_dotenv(), override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID   = os.getenv("ASSISTANT_ID")
AUTH_TOKEN     = os.getenv("AUTH_TOKEN", "dev-token")
ASSISTANT_TIMEOUT_SECONDS = float(os.getenv("ASSISTANT_TIMEOUT_SECONDS", "12"))

try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except Exception:
    client = None

app = FastAPI(title="ARIA Webhook")
security = HTTPBearer()

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials or ""
    if token != AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------

class AssistRequest(BaseModel):
    # Aceita 'input' OU 'user_text' para compatibilidade
    input: Optional[str] = None
    user_text: Optional[str] = None
    thread_id: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None

class AssistResponse(BaseModel):
    reply_text: str
    route: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    next_action: Optional[str] = None
    tags: Optional[List[str]] = None
    thread_id: str

# ---------------------------------------------------------------------------
# Regras de negócio: triagem + volumetria
# ---------------------------------------------------------------------------

def classify_route(user_text: str, v: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, str], Optional[str]]:
    """Decide rota (envio/recebimento) e, se envio, classifica volumetria.
    Retorna: (route, variables_out, next_action)
    """
    t = (user_text or "").lower()
    route: Optional[str] = None
    vars_out: Dict[str, str] = {}
    next_action: Optional[str] = None

    # 1) Preferir fluxo explícito
    fp = str(v.get("fluxo_path", "")).strip().lower()
    if fp in {"envio", "recebimento"}:
        route = fp
    else:
        # 2) Heurística simples
        if any(k in t for k in ["recebi", "receb", "chegou", "abriu", "abertura", "li", "confirmacao de leitura"]):
            route = "recebimento"
        elif any(k in t for k in ["enviar", "envio", "mandar", "disparar", "disparo", "quero enviar"]):
            route = "envio"

    # 3) Se envio, calcular volumetria
    if route == "envio":
        limiar = int(v.get("VOLUME_ALTO_LIMIAR", 1200))
        vol_src = str(v.get("lead_volumetria", v.get("lead_duvida", ""))).lower()

        n = None
        m = re.findall(r"\d{1,3}(?:[\.,]\d{3})+|\d+", vol_src)
        if m:
            token = re.sub(r"[^\d]", "", m[-1])
            if token:
                n = int(token)

        kw_high = re.search(r"(alto volume|grande volume|massivo|lote|mil|1k|1000\+|acima de|>\s*1000)", vol_src)
        is_high = (n is not None and n >= limiar) or bool(kw_high)

        vars_out.update({
            "volume_num": str(n or ""),
            "volume_alto": "true" if is_high else "false",
            "volume_class": "alto" if is_high else "baixo",
        })
        next_action = "schedule" if is_high else "buy_credits"

    return route, vars_out, next_action

# ---------------------------------------------------------------------------
# Utilidades OpenAI (opcionais)
# ---------------------------------------------------------------------------

def wait_run(thread_id: str, run_id: str, timeout_seconds: Optional[float] = None):
    if client is None:
        return None
    deadline: Optional[float] = None
    if timeout_seconds is not None and timeout_seconds > 0:
        deadline = time.time() + timeout_seconds
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status in ("completed", "failed", "cancelled", "expired"):
            return run
        if run.status == "requires_action":
            return run
        if deadline is not None and time.time() >= deadline:
            return None
        time.sleep(0.6)


def last_assistant_message(thread_id: str) -> str:
    if client is None:
        return ""
    msgs = client.beta.threads.messages.list(thread_id=thread_id)
    for msg in msgs.data:
        if getattr(msg, "role", "") == "assistant":
            try:
                return msg.content[0].text.value
            except Exception:
                continue
    return ""

# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@app.post("/assist/routing", response_model=AssistResponse)
def assist_routing(req: AssistRequest, _tok: str = Depends(require_auth)):
    try:
        user_text = (req.input or req.user_text or "").strip()
        v_in: Dict[str, Any] = dict(req.variables or {})

        # Regras determinísticas de negócio
        route, vars_out, next_action = classify_route(user_text, v_in)

        # Thread
        if req.thread_id:
            thread_id = req.thread_id
        else:
            thread_id = f"thread_{secrets.token_hex(8)}"
            if client is not None:
                thread_id = client.beta.threads.create().id

        # Se houver OpenAI Assistant, registra mensagem e executa run
        reply_text = ""
        if client is not None and ASSISTANT_ID:
            try:
                client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_text)
                run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=ASSISTANT_ID)
                run = wait_run(thread_id, run.id, timeout_seconds=ASSISTANT_TIMEOUT_SECONDS)
                reply_text = (last_assistant_message(thread_id) or reply_text)
            except Exception:
                # Em caso de erro/timeout no Assistant, segue com fallback determinístico
                pass

        # Fallback de resposta se não houver assistant ou não retornou texto
        if not reply_text:
            if route == "recebimento":
                reply_text = (
                    "Entendi que você recebeu uma notificação. A AR Online é o meio de envio; "
                    "o conteúdo deve ser tratado diretamente com o remetente indicado na mensagem."
                )
            elif route == "envio":
                reply_text = (
                    "Certo! Para indicar o melhor caminho, me informe uma estimativa do volume mensal de envios (ex.: 50, 300, 1500)."
                )
            else:
                reply_text = "Como posso te ajudar hoje?"

        return AssistResponse(
            reply_text=reply_text,
            route=route,
            variables=vars_out or None,
            confidence=0.75 if route else None,
            next_action=next_action,
            tags=[],
            thread_id=thread_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/healthz")
def healthz():
    return {"ok": True}
