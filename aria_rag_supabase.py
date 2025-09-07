"""
ARIA • Script Python de RAG com Supabase (pgvector)
--------------------------------------------------
Este utilitário ajuda a **ingestar** conteúdos com embeddings no Supabase
(e tabelas com pgvector) e também a **consultar** os trechos mais relevantes
para montar o contexto do RAG da ARIA.

✅ O que ele faz
- Lê texto (arquivo único, pasta com .txt/.md, ou JSONL com registros)
- Quebra em *chunks* determinísticos
- Gera embeddings com OpenAI (`text-embedding-3-small` por padrão)
- Sobe para a tabela `aria_chunks` via REST
- Consulta semântica (kNN) via função RPC `match_aria_chunks` (sugerida abaixo)

⚙️ Pré‑requisitos
1) **Criar a tabela e a função no Supabase — passo a passo**
   1. Acesse o seu projeto no **Supabase** → **SQL Editor** → **New Query**.
   2. (Primeira vez?) Confirme que a extensão **pgvector** está disponível no schema **public**.
   3. **Ajuste a dimensão** do vetor conforme o modelo de embedding (ex.: `text-embedding-3-small` = **1536**).
   4. Cole o bloco SQL abaixo **inteiro** e clique em **Run**.
   5. Verifique no **Table Editor** se a tabela `aria_chunks` foi criada e o índice `ivfflat` existe.
   6. (Opcional) **RLS**: mantenha **desativado** por enquanto; se ativar, o **Service Role** (chave usada pelo backend) ignora políticas, mas recomenda‑se criar políticas explícitas para outros papéis.
   7. (Opcional) Teste rápido do RPC: depois de ingerir dados, chame a função `match_aria_chunks` via **SQL** ou **REST**.

```
create extension if not exists vector;

-- AJUSTE a dimensão para o modelo escolhido (1536 = text-embedding-3-small)
create table if not exists aria_chunks (
  id uuid primary key default gen_random_uuid(),
  source text,
  doc_id text,
  chunk_index int,
  content text,
  metadata jsonb,
  embedding vector(1536),
  created_at timestamptz default now()
);
create index if not exists aria_chunks_embedding_idx on aria_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);

create or replace function match_aria_chunks(
  query_embedding vector(1536),
  match_count int default 5,
  filter_source text default null
)
returns table(
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language sql stable as $$
  select
    c.id,
    c.content,
    c.metadata,
    1 - (c.embedding <=> query_embedding) as similarity
  from aria_chunks c
  where filter_source is null or c.source = filter_source
  order by c.embedding <=> query_embedding
  limit match_count;
$$;
```

2) Variáveis de ambiente (coloque num `.env` local ou no ambiente do VS Code):
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY` (⚠️ usar somente em backend/seguro)
- `OPENAI_API_KEY`
- (opcional) `EMBEDDING_MODEL` (padrão `text-embedding-3-small`)
- (opcional) `EMBEDDING_DIM` (padrão `1536`)
- (opcional) `ARIA_TABLE` (padrão `aria_chunks`)

3) Dependências (requirements):
```
python-dotenv>=1.0.1
openai>=1.30.0
requests>=2.32.0
tiktoken>=0.7.0
```

▶️ Uso rápido (no terminal do VS Code)
```
# Ingestar um arquivo .md
python aria_rag_supabase.py ingest --path docs/faq.md --source faq --doc-id faq_v1

# Ingestar todos .md/.txt de uma pasta (cada arquivo vira um doc_id)
python aria_rag_supabase.py ingest --path docs/ --source site

# Ingestar via JSONL (um registro por linha: {"doc_id":..., "content":..., "metadata":{}})
python aria_rag_supabase.py ingest --jsonl dados.jsonl --source faq

# Consultar (RAG)
python aria_rag_supabase.py query --question "Como funciona a AR Online?" --k 5 --filter-source faq
```
"""

from __future__ import annotations
import os
import re
import json
import math
import argparse
from dataclasses import dataclass
from typing import Iterable, List, Dict, Any, Optional

import requests
from dotenv import load_dotenv

try:
    # OpenAI SDK (>=1.0)
    from openai import OpenAI
except Exception as e:  # pragma: no cover
    OpenAI = None  # type: ignore

# ---------------------------
# Config & Helpers
# ---------------------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))
ARIA_TABLE = os.getenv("ARIA_TABLE", "aria_chunks")

HEADERS_JSON = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

if not SUPABASE_URL or not SUPABASE_KEY:
    raise SystemExit("⚠️ Defina SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no ambiente.")
if not OPENAI_API_KEY:
    raise SystemExit("⚠️ Defina OPENAI_API_KEY no ambiente.")

# ---------------------------
# Chunking (determinístico e simples)
# ---------------------------
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    # split básico por pontuação
    parts = SENTENCE_SPLIT_RE.split(text)
    # garante que nenhuma sentença escapa vazia
    return [p.strip() for p in parts if p.strip()]


def chunk_text(text: str, max_tokens: int = 350, overlap_tokens: int = 50) -> List[str]:
    """Chunking aproximado por contagem de caracteres (proxy de tokens).
    Para uso em FAQ/documentação funciona bem e é estável.
    """
    approx_token_ratio = 4  # ~4 chars por token (aprox.)
    max_chars = max_tokens * approx_token_ratio
    overlap_chars = overlap_tokens * approx_token_ratio

    sents = split_sentences(text)
    chunks: List[str] = []
    buf: List[str] = []
    cur_len = 0

    def flush():
        nonlocal buf, cur_len
        if buf:
            chunks.append(" ".join(buf).strip())
            # prepara overlap
            joined = " ".join(buf)
            tail = joined[-overlap_chars:]
            buf = [tail] if tail else []
            cur_len = len(tail)

    for s in sents:
        s_len = len(s)
        if cur_len + s_len + 1 > max_chars:
            flush()
        buf.append(s)
        cur_len += s_len + 1
    if buf:
        chunks.append(" ".join(buf).strip())
    # drop possíveis vazios
    return [c for c in chunks if c]

# ---------------------------
# Embeddings
# ---------------------------

def get_openai_client() -> OpenAI:
    if OpenAI is None:
        raise RuntimeError("Biblioteca openai não disponível. Instale 'openai>=1.30.0'.")
    return OpenAI(api_key=OPENAI_API_KEY)


def embed_texts(texts: List[str], model: str = EMBEDDING_MODEL) -> List[List[float]]:
    client = get_openai_client()
    # A API do SDK 1.x aceita lista em 'input'
    resp = client.embeddings.create(model=model, input=texts)
    # Garante a ordem original
    vectors = [d.embedding for d in resp.data]
    # Sanidade: todos com dimensão correta
    for v in vectors:
        if len(v) != EMBEDDING_DIM:
            raise ValueError(
                f"Dimensão incorreta do embedding: {len(v)} (esperado {EMBEDDING_DIM})."
            )
    return vectors

# ---------------------------
# Supabase REST: upsert & query (RPC)
# ---------------------------

def supabase_upsert_chunks(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    url = f"{SUPABASE_URL}/rest/v1/{ARIA_TABLE}"
    r = requests.post(url, headers=HEADERS_JSON, data=json.dumps(rows))
    if r.status_code >= 300:
        raise RuntimeError(f"Erro upsert: {r.status_code} -> {r.text}")
    return r.json()


def supabase_match(query_embedding: List[float], k: int = 5, filter_source: Optional[str] = None) -> List[Dict[str, Any]]:
    url = f"{SUPABASE_URL}/rest/v1/rpc/match_aria_chunks"
    payload = {
        "query_embedding": query_embedding,
        "match_count": int(k),
        "filter_source": filter_source,
    }
    r = requests.post(url, headers=HEADERS_JSON, data=json.dumps(payload))
    if r.status_code >= 300:
        raise RuntimeError(f"Erro RPC match: {r.status_code} -> {r.text}")
    return r.json()

# ---------------------------
# Ingestão
# ---------------------------

@dataclass
class IngestItem:
    doc_id: str
    content: str
    metadata: Dict[str, Any]


def iter_files(path: str) -> Iterable[str]:
    exts = {".txt", ".md"}
    if os.path.isfile(path):
        yield path
    else:
        for root, _, files in os.walk(path):
            for f in files:
                if os.path.splitext(f)[1].lower() in exts:
                    yield os.path.join(root, f)


def load_items_from_path(path: str) -> List[IngestItem]:
    items: List[IngestItem] = []
    for fp in iter_files(path):
        with open(fp, "r", encoding="utf-8") as fh:
            txt = fh.read()
        doc_id = os.path.relpath(fp, start=os.path.dirname(path) or ".").replace(os.sep, "/")
        items.append(IngestItem(doc_id=doc_id, content=txt, metadata={"path": fp}))
    return items


def load_items_from_jsonl(jsonl_path: str) -> List[IngestItem]:
    items: List[IngestItem] = []
    with open(jsonl_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            obj = json.loads(line)
            items.append(
                IngestItem(
                    doc_id=obj.get("doc_id") or obj.get("id") or "doc",
                    content=obj.get("content", ""),
                    metadata=obj.get("metadata", {}),
                )
            )
    return items


def ingest(path: Optional[str], jsonl: Optional[str], source: str, explicit_doc_id: Optional[str] = None, max_tokens: int = 350) -> None:
    # Carrega itens
    if jsonl:
        items = load_items_from_jsonl(jsonl)
    elif path:
        items = load_items_from_path(path)
    else:
        raise SystemExit("Informe --path ou --jsonl para ingestão.")

    # Se o usuário passou --doc-id para arquivo único, aplica
    if explicit_doc_id and len(items) == 1:
        items[0].doc_id = explicit_doc_id

    for it in items:
        chunks = chunk_text(it.content, max_tokens=max_tokens)
        if not chunks:
            continue
        vectors = embed_texts(chunks)
        rows = []
        for idx, (ch, emb) in enumerate(zip(chunks, vectors)):
            rows.append(
                {
                    "source": source,
                    "doc_id": it.doc_id,
                    "chunk_index": idx,
                    "content": ch,
                    "metadata": it.metadata,
                    "embedding": emb,
                }
            )
        saved = supabase_upsert_chunks(rows)
        print(f"✔ Ingestado: {it.doc_id} | chunks: {len(saved)}")

# ---------------------------
# Consulta (RAG)
# ---------------------------

def query(question: str, k: int = 5, filter_source: Optional[str] = None) -> None:
    vectors = embed_texts([question])
    qv = vectors[0]
    hits = supabase_match(qv, k=k, filter_source=filter_source)

    print("\nTop trechos:")
    for i, h in enumerate(hits, 1):
        sim = float(h.get("similarity", 0))
        meta = h.get("metadata") or {}
        print("-" * 80)
        print(f"[{i}] similarity={sim:.4f} | metadata={json.dumps(meta, ensure_ascii=False)}")
        print(h.get("content", "")[:1000])

    # Sugerir um template de contexto para colar no prompt
    context_blobs = [h.get("content", "") for h in hits]
    context = "\n\n".join(f"[{i+1}] " + c for i, c in enumerate(context_blobs))
    print("\n--- PROMPT SUGERIDO ---\n")
    print("CONTEXTO:\n" + context)
    print("\nINSTRUÇÕES AO MODELO:\n- Responda em pt-BR.\n- Use APENAS o CONTEXTO. Se algo não estiver no contexto, diga que não encontrou e ofereça encaminhar ao time.\n- Seja objetivo e cite a fonte (doc_id/chunk_index) quando útil.")

# ---------------------------
# CLI
# ---------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ARIA • RAG com Supabase (pgvector)")
    sub = p.add_subparsers(dest="cmd", required=True)

    # ingest
    pi = sub.add_parser("ingest", help="Ingestar arquivos/pastas ou JSONL")
    pi.add_argument("--path", type=str, help="Arquivo único (.txt/.md) ou pasta", default=None)
    pi.add_argument("--jsonl", type=str, help="Caminho para JSONL com registros", default=None)
    pi.add_argument("--source", type=str, required=True, help="Fonte lógica (faq, site, pdf…)")
    pi.add_argument("--doc-id", type=str, default=None, help="Força doc_id quando houver 1 arquivo")
    pi.add_argument("--max-tokens", type=int, default=350, help="Tamanho de chunk aproximado")

    # query
    pq = sub.add_parser("query", help="Consultar trechos relevantes (RAG)")
    pq.add_argument("--question", type=str, required=True, help="Pergunta do usuário")
    pq.add_argument("--k", type=int, default=5, help="Quantidade de trechos")
    pq.add_argument("--filter-source", type=str, default=None, help="Filtrar por source")

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "ingest":
        ingest(
            path=args.path,
            jsonl=args.jsonl,
            source=args.source,
            explicit_doc_id=getattr(args, "doc_id", None),
            max_tokens=getattr(args, "max_tokens", 350),
        )
    elif args.cmd == "query":
        query(question=args.question, k=args.k, filter_source=args.filter_source)
    else:  # pragma: no cover
        parser.print_help()


if __name__ == "__main__":
    main()
import logging
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# 1) Load environment with override for local dev
load_dotenv(override=True)

# 2) Minimal, idempotent logging setup
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
logger = logging.getLogger(__name__)

# 3) Timeouts for outbound HTTP calls (seconds)
DEFAULT_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "15"))

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore


def http_post_json(url: str, payload: Dict[str, Any], timeout: Optional[float] = None) -> Any:
    """POST JSON with timeout and basic error handling.

    Returns parsed JSON or raises on errors/timeouts.
    """
    if requests is None:
        raise RuntimeError("'requests' not available; install it or adapt the client")
    to = timeout if timeout is not None else DEFAULT_TIMEOUT
    try:
        resp = requests.post(url, json=payload, timeout=to)
        resp.raise_for_status()
        return resp.json()
    except requests.Timeout as exc:  # type: ignore[attr-defined]
        logger.error("RAG timeout calling %s: %s", url, exc)
        raise
    except requests.RequestException as exc:  # type: ignore[attr-defined]
        logger.error("RAG request error calling %s: %s", url, exc)
        raise
