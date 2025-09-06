import os
import re
import time
import secrets
import hashlib
import uuid
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
from typing import Any, Dict, Optional, Tuple, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Configurações TTS
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "openai")  # openai|azure|polly|gcloud|eleven
TTS_VOICE = os.getenv("TTS_VOICE", "alloy")  # ex.: "alloy", "br-giovanna", "Vitoria", etc.
TTS_FORMAT = os.getenv("TTS_FORMAT", "mp3")  # mp3 ou ogg
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://api.sua-aria.com")  # onde o arquivo ficará acessível
AUDIO_STORAGE = os.getenv("AUDIO_STORAGE", "local")  # local|s3

# Configurações S3 (se AUDIO_STORAGE=s3)
S3_BUCKET = os.getenv("S3_BUCKET", "aria-tts")
S3_REGION = os.getenv("S3_REGION", "sa-east-1")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")

try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except Exception:
    client = None

app = FastAPI(title="ARIA Webhook")
security = HTTPBearer()

# Configurar arquivos estáticos para áudio (apenas se armazenamento for local)
if AUDIO_STORAGE == "local":
    audio_dir = Path("audio_files")
    audio_dir.mkdir(exist_ok=True)
    app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")

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

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    format: Optional[str] = None
    provider: Optional[str] = None

class TTSResponse(BaseModel):
    audio_url: str
    file_id: str
    provider: str
    voice: str
    format: str
    text_hash: str

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
# Utilidades TTS
# ---------------------------------------------------------------------------

def generate_file_id(text: str, voice: str, provider: str) -> str:
    """Gera um ID único baseado no texto, voz e provedor"""
    content = f"{text}|{voice}|{provider}"
    return hashlib.md5(content.encode()).hexdigest()

def save_audio_local(audio_data: bytes, file_id: str, format: str) -> str:
    """Salva áudio localmente e retorna o caminho"""
    audio_dir = Path("audio_files")
    audio_dir.mkdir(exist_ok=True)

    filename = f"{file_id}.{format}"
    filepath = audio_dir / filename

    with open(filepath, "wb") as f:
        f.write(audio_data)

    return f"{PUBLIC_BASE_URL}/audio/{filename}"

def save_audio_s3(audio_data: bytes, file_id: str, format: str) -> str:
    """Salva áudio no S3 e retorna a URL"""
    try:
        import boto3
        from botocore.exceptions import ClientError

        s3_client = boto3.client(
            's3',
            region_name=S3_REGION,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY
        )

        filename = f"{file_id}.{format}"
        s3_key = f"tts/{filename}"

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=audio_data,
            ContentType=f"audio/{format}"
        )

        return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"

    except ImportError:
        raise HTTPException(status_code=500, detail="boto3 não instalado para armazenamento S3")
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no S3: {str(e)}")

def save_audio(audio_data: bytes, file_id: str, format: str) -> str:
    """Salva áudio usando o método configurado (local ou S3)"""
    if AUDIO_STORAGE == "s3":
        return save_audio_s3(audio_data, file_id, format)
    else:
        return save_audio_local(audio_data, file_id, format)

def tts_openai(text: str, voice: str, format: str) -> bytes:
    """Converte texto em áudio usando OpenAI TTS"""
    if client is None:
        raise HTTPException(status_code=500, detail="Cliente OpenAI não configurado")

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format=format
        )
        return response.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro OpenAI TTS: {str(e)}")

def tts_azure(text: str, voice: str, format: str) -> bytes:
    """Converte texto em áudio usando Azure Cognitive Services"""
    try:
        import requests

        # Configurações Azure (precisa ser configurado via env vars)
        azure_key = os.getenv("AZURE_SPEECH_KEY")
        azure_region = os.getenv("AZURE_SPEECH_REGION")

        if not azure_key or not azure_region:
            raise HTTPException(status_code=500, detail="Azure Speech não configurado")

        url = f"https://{azure_region}.tts.speech.microsoft.com/cognitiveservices/v1"
        headers = {
            "Ocp-Apim-Subscription-Key": azure_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": f"audio-16khz-128kbitrate-mono-{format}"
        }

        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='pt-BR'>
            <voice name='{voice}'>
                {text}
            </voice>
        </speak>
        """

        response = requests.post(url, headers=headers, data=ssml.encode('utf-8'))
        response.raise_for_status()
        return response.content

    except ImportError:
        raise HTTPException(status_code=500, detail="requests não instalado para Azure TTS")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro Azure TTS: {str(e)}")

def tts_polly(text: str, voice: str, format: str) -> bytes:
    """Converte texto em áudio usando AWS Polly"""
    try:
        import boto3
        from botocore.exceptions import ClientError

        polly_client = boto3.client(
            'polly',
            region_name=S3_REGION,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY
        )

        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat=format,
            VoiceId=voice
        )

        return response['AudioStream'].read()

    except ImportError:
        raise HTTPException(status_code=500, detail="boto3 não instalado para AWS Polly")
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Erro AWS Polly: {str(e)}")

def tts_gcloud(text: str, voice: str, format: str) -> bytes:
    """Converte texto em áudio usando Google Cloud Text-to-Speech"""
    try:
        from google.cloud import texttospeech

        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice_config = texttospeech.VoiceSelectionParams(
            language_code="pt-BR",
            name=voice
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=getattr(texttospeech.AudioEncoding, format.upper())
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_config,
            audio_config=audio_config
        )

        return response.audio_content

    except ImportError:
        raise HTTPException(status_code=500, detail="google-cloud-texttospeech não instalado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro Google Cloud TTS: {str(e)}")

def tts_eleven(text: str, voice: str, format: str) -> bytes:
    """Converte texto em áudio usando ElevenLabs"""
    try:
        import requests

        eleven_key = os.getenv("ELEVENLABS_API_KEY")
        if not eleven_key:
            raise HTTPException(status_code=500, detail="ElevenLabs API key não configurada")

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
        headers = {
            "Accept": f"audio/{format}",
            "Content-Type": "application/json",
            "xi-api-key": eleven_key
        }

        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.content

    except ImportError:
        raise HTTPException(status_code=500, detail="requests não instalado para ElevenLabs TTS")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ElevenLabs TTS: {str(e)}")

def generate_tts_audio(text: str, voice: str, format: str, provider: str) -> bytes:
    """Gera áudio usando o provedor especificado"""
    provider = provider.lower()

    if provider == "openai":
        return tts_openai(text, voice, format)
    elif provider == "azure":
        return tts_azure(text, voice, format)
    elif provider == "polly":
        return tts_polly(text, voice, format)
    elif provider == "gcloud":
        return tts_gcloud(text, voice, format)
    elif provider == "eleven":
        return tts_eleven(text, voice, format)
    else:
        raise HTTPException(status_code=400, detail=f"Provedor TTS não suportado: {provider}")

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


@app.post("/tts", response_model=TTSResponse)
def text_to_speech(req: TTSRequest, _tok: str = Depends(require_auth)):
    """Converte texto em áudio usando o provedor TTS configurado"""
    try:
        # Usar configurações da requisição ou fallback para configurações globais
        provider = req.provider or TTS_PROVIDER
        voice = req.voice or TTS_VOICE
        format = req.format or TTS_FORMAT

        # Validar formato
        if format not in ["mp3", "ogg"]:
            raise HTTPException(status_code=400, detail="Formato deve ser 'mp3' ou 'ogg'")

        # Gerar ID único para o arquivo
        file_id = generate_file_id(req.text, voice, provider)

        # Gerar áudio usando o provedor especificado
        audio_data = generate_tts_audio(req.text, voice, format, provider)

        # Salvar áudio
        audio_url = save_audio(audio_data, file_id, format)

        # Gerar hash do texto para cache
        text_hash = hashlib.md5(req.text.encode()).hexdigest()

        return TTSResponse(
            audio_url=audio_url,
            file_id=file_id,
            provider=provider,
            voice=voice,
            format=format,
            text_hash=text_hash
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/healthz")
def healthz():
    return {"ok": True}
