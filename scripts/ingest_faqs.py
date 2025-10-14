from __future__ import annotations

import argparse
import json
import os
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


def _lazy_imports():
    try:
        from PyPDF2 import PdfReader  # type: ignore
    except Exception as e:  # pragma: no cover
        raise SystemExit("Missing dependency: PyPDF2. Install with `pip install PyPDF2`.") from e

    try:
        from slugify import slugify  # type: ignore
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "Missing dependency: python-slugify. Install with `pip install python-slugify`."
        ) from e

    try:
        from unidecode import unidecode  # type: ignore
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "Missing dependency: Unidecode. Install with `pip install Unidecode`."
        ) from e

    try:
        from tqdm import tqdm  # type: ignore
    except Exception:  # pragma: no cover
        # Fallback progress shim
        def tqdm(x, **_):
            return x

    return PdfReader, slugify, unidecode, tqdm


def _get_openai_client():
    try:
        from openai import OpenAI  # type: ignore
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "Missing dependency: openai>=1.0. Install with `pip install openai`."
        ) from e
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Set OPENAI_API_KEY in your environment.")
    return OpenAI(api_key=api_key)


def _supabase_headers() -> dict[str, str]:
    url = (os.getenv("SUPABASE_URL", "") or "").rstrip("/")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or ""
    if not url or not key:
        raise SystemExit("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your environment.")
    return {
        "_base_url": url,  # sentinel for building endpoints
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def upsert_chunks(rows: list[dict[str, Any]], table: str = "aria_chunks") -> list[dict[str, Any]]:
    import requests

    headers = _supabase_headers()
    base_url = headers.pop("_base_url")
    url = f"{base_url}/rest/v1/{table}"
    r = requests.post(url, headers=headers, data=json.dumps(rows), timeout=60)
    if r.status_code >= 300:
        raise RuntimeError(f"Supabase upsert failed: {r.status_code} -> {r.text}")
    try:
        return r.json()
    except Exception:
        return []


def chunk_text_words(text: str, size: int, overlap: int) -> list[str]:
    words = text.split()
    out: list[str] = []
    i = 0
    n = len(words)
    if size <= 0:
        return [text.strip()]
    while i < n:
        j = min(n, i + size)
        out.append(" ".join(words[i:j]))
        if j == n:
            break
        # move by size-overlap tokens; ensure progress
        step = max(1, size - max(0, overlap))
        i += step
    return out


@dataclass
class PdfChunk:
    source: str
    doc_id: str
    page: int
    chunk_index: int
    content: str
    metadata: dict[str, Any]


def extract_pdf_chunks(
    pdf_path: Path, *, source: str, namespace: str | None, chunk_tokens: int, overlap_tokens: int
) -> list[PdfChunk]:
    PdfReader, slugify, unidecode, _tqdm = _lazy_imports()
    reader = PdfReader(pdf_path.as_posix())
    base = slugify(pdf_path.stem)
    chunks: list[PdfChunk] = []
    for p, page in enumerate(reader.pages, start=1):
        txt = (page.extract_text() or "").strip()
        if not txt:
            continue
        cleaned = unidecode(" ".join(txt.split()))
        parts = chunk_text_words(cleaned, chunk_tokens, overlap_tokens)
        for k, part in enumerate(parts):
            meta: dict[str, Any] = {
                "page": p,
                "tags": [source],
                "updated_at": datetime.now(UTC).isoformat(),
            }
            if namespace:
                meta["namespace"] = namespace
            chunks.append(
                PdfChunk(
                    source=source,
                    doc_id=f"{base}.pdf",
                    page=p,
                    chunk_index=k,
                    content=part,
                    metadata=meta,
                )
            )
    return chunks


def embed_texts(texts: list[str], model: str) -> list[list[float]]:
    client = _get_openai_client()
    resp = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]


def batched(iterable: Iterable[Any], batch_size: int) -> Iterable[list[Any]]:
    batch: list[Any] = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def ingest_pdfs(
    paths: list[Path],
    *,
    source: str,
    namespace: str | None,
    model: str,
    chunk_tokens: int,
    overlap_tokens: int,
    batch: int,
    table: str,
) -> None:
    _, _, _, tqdm = _lazy_imports()
    all_chunks: list[PdfChunk] = []
    for p in tqdm(paths, desc="Reading PDFs"):
        all_chunks.extend(
            extract_pdf_chunks(
                p,
                source=source,
                namespace=namespace,
                chunk_tokens=chunk_tokens,
                overlap_tokens=overlap_tokens,
            )
        )

    if not all_chunks:
        print("No chunks extracted.")
        return

    # Embed and upsert in batches
    total = len(all_chunks)
    idx = 0
    for group in tqdm(list(batched(all_chunks, batch)), desc="Embedding + Upsert"):
        texts = [c.content for c in group]
        vectors = embed_texts(texts, model=model)
        # Default row shape (aria_chunks schema)
        rows = []
        for c, emb in zip(group, vectors, strict=False):
            rows.append(
                {
                    "source": c.source,
                    "doc_id": c.doc_id,
                    "chunk_index": c.chunk_index,
                    "content": c.content,
                    "metadata": c.metadata,
                    "embedding": emb,
                }
            )

        # Try upsert; if table lacks doc_id/chunk_index (e.g., rag_chunks),
        # fallback to a reduced schema and stash identifiers in metadata.
        try:
            saved = upsert_chunks(rows, table=table)
        except RuntimeError as e:
            msg = str(e)
            missing_doc = "doc_id" in msg.lower()
            missing_chunk = "chunk_index" in msg.lower()
            if missing_doc or missing_chunk:
                rows_min: list[dict[str, Any]] = []
                for c, emb in zip(group, vectors, strict=False):
                    meta2 = dict(c.metadata or {})
                    # Preserve identifiers in metadata when table lacks columns
                    if missing_doc:
                        meta2.setdefault("doc_id", c.doc_id)
                    if missing_chunk:
                        meta2.setdefault("chunk_index", c.chunk_index)
                    rows_min.append(
                        {
                            "source": c.source,
                            "content": c.content,
                            "metadata": meta2,
                            **({"namespace": namespace} if namespace else {}),
                            "embedding": emb,
                        }
                    )
                try:
                    saved = upsert_chunks(rows_min, table=table)
                except RuntimeError as e2:
                    # If table also lacks 'metadata', drop it and retry once more
                    if "metadata" in str(e2).lower():
                        rows_min2: list[dict[str, Any]] = []
                        for c, emb in zip(group, vectors, strict=False):
                            rows_min2.append(
                                {
                                    "source": c.source,
                                    "content": c.content,
                                    **({"namespace": namespace} if namespace else {}),
                                    "embedding": emb,
                                }
                            )
                        saved = upsert_chunks(rows_min2, table=table)
                    else:
                        raise
            else:
                raise
        idx += len(saved) if saved else len(rows)
        print(f"Progress: {idx}/{total} saved")

    print(f"Upsert concluido: {total} chunks (source={source}, namespace={namespace or '-'})")


def parse_args() -> argparse.Namespace:
    load_dotenv(override=True)
    p = argparse.ArgumentParser(description="Ingest FAQs from PDFs into Supabase (pgvector)")
    p.add_argument("paths", nargs="+", help="PDF files or directories containing PDFs")
    p.add_argument(
        "--source", default=os.getenv("RAG_DEFAULT_SOURCE", "faq"), help="Logical source label"
    )
    p.add_argument(
        "--namespace",
        default=os.getenv("RAG_NAMESPACE", None),
        help="Optional namespace tag saved in metadata",
    )
    p.add_argument(
        "--model",
        default=os.getenv("EMBEDDING_MODEL", os.getenv("OPENAI_MODEL", "text-embedding-3-small")),
    )
    p.add_argument("--chunk-tokens", type=int, default=int(os.getenv("CHUNK_TOKENS", "450")))
    p.add_argument("--overlap-tokens", type=int, default=int(os.getenv("OVERLAP_TOKENS", "80")))
    p.add_argument(
        "--batch",
        type=int,
        default=int(os.getenv("UPSERT_BATCH", "64")),
        help="Batch size for embed/upsert",
    )
    p.add_argument(
        "--table",
        type=str,
        default=os.getenv("ARIA_TABLE", "aria_chunks"),
        help="Target table name (can be schema-qualified, e.g. rag.aria_chunks)",
    )
    return p.parse_args()


def collect_pdf_paths(args_paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in args_paths:
        path = Path(p)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.pdf")))
        elif path.is_file() and path.suffix.lower() == ".pdf":
            files.append(path)
    # Deduplicate while preserving order
    seen: set[str] = set()
    uniq: list[Path] = []
    for f in files:
        sp = f.resolve().as_posix()
        if sp not in seen:
            seen.add(sp)
            uniq.append(f)
    return uniq


def main() -> None:
    args = parse_args()
    pdfs = collect_pdf_paths(args.paths)
    if not pdfs:
        raise SystemExit("No PDF files found.")
    ingest_pdfs(
        pdfs,
        source=args.source,
        namespace=args.namespace,
        model=args.model,
        chunk_tokens=max(1, args.chunk_tokens),
        overlap_tokens=max(0, args.overlap_tokens),
        batch=max(1, args.batch),
        table=args.table,
    )


if __name__ == "__main__":
    main()
