from __future__ import annotations

import argparse
import math
import os
from collections.abc import Iterable
from typing import Any

import requests
from dotenv import load_dotenv


def get_openai_client():
    try:
        from openai import OpenAI  # type: ignore
    except Exception as e:  # pragma: no cover
        raise SystemExit("Missing dependency: openai. pip install openai") from e
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Set OPENAI_API_KEY in your environment.")
    return OpenAI(api_key=api_key)


def supabase_get_rows(
    table: str, *, source: str | None, namespace: str | None
) -> list[dict[str, Any]]:
    url = (os.getenv("SUPABASE_URL", "") or "").rstrip("/")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or ""
    if not url or not key:
        raise SystemExit("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your environment.")
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
    }
    # Be conservative: some tables may not have 'metadata'.
    params: dict[str, str] = {"select": "content,embedding,source,namespace"}
    if source:
        params["source"] = f"eq.{source}"
    if namespace:
        params["namespace"] = f"eq.{namespace}"
    resp = requests.get(f"{url}/rest/v1/{table}", headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()  # type: ignore[no-any-return]


def embed_texts(texts: list[str], model: str) -> list[list[float]]:
    client = get_openai_client()
    out = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in out.data]


def cosine(a: Iterable[float], b: Iterable[float]) -> float:
    ax = list(a)
    bx = list(b)
    dot = sum(x * y for x, y in zip(ax, bx, strict=False))
    na = math.sqrt(sum(x * x for x in ax))
    nb = math.sqrt(sum(y * y for y in bx))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def main() -> None:
    load_dotenv(override=True)
    p = argparse.ArgumentParser(description="Quick RAG check against Supabase table (no RPC)")
    p.add_argument("--question", required=True)
    p.add_argument("--table", default=os.getenv("ARIA_TABLE", "rag_chunks"))
    p.add_argument("--model", default=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--source", default=None)
    p.add_argument("--namespace", default=os.getenv("RAG_NAMESPACE", None))
    args = p.parse_args()

    rows = supabase_get_rows(args.table, source=args.source, namespace=args.namespace)
    if not rows:
        print("No rows returned from Supabase with provided filters.")
        return
    qv = embed_texts([args.question], model=args.model)[0]

    scored: list[tuple[float, dict[str, Any]]] = []
    for r in rows:
        emb = r.get("embedding") or []
        try:
            sim = cosine(qv, emb)
        except Exception:
            continue
        scored.append((sim, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[: max(1, int(args.k))]
    print(
        f"Top {len(top)} hits (table={args.table}, source={args.source or '-'}, namespace={args.namespace or '-'})\n"
    )
    for i, (sim, r) in enumerate(top, 1):
        content = (r.get("content") or "")[:500]
        print(
            f"[{i}] sim={sim:.4f} | source={r.get('source')} | ns={r.get('namespace')}\n{content}\n---"
        )


if __name__ == "__main__":
    main()
