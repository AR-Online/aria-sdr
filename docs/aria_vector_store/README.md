
# ARIA Vector Store (TF‑IDF)

Este pacote contém um "vector store" local com os documentos do projeto.
Você pode usá‑lo diretamente em Python para POC/benchmarks ou enviar os PDFs
originais para um Vector Store do OpenAI Assistants (os embeddings serão gerados no servidor).

## Arquivos
- `chunks.jsonl`: chunks com metadados (id, text, source_file, title, page, tags).
- `tfidf_index.pkl`: matriz TF‑IDF (scipy csr_matrix).
- `vectorizer.pkl`: TfidfVectorizer fitado.
- PDFs utilizados: FAQ Completo – AR Online & ARIA.pdf, Aria — Guia De Produto (não Técnico).pdf, Contexto Completo Projeto Ar Online (atualizado Jul 2025).pdf.

## Exemplo de uso (Python)
```python
import pickle, json
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

base = Path("aria_vector_store")
X = pickle.load(open(base / "tfidf_index.pkl", "rb"))
vectorizer = pickle.load(open(base / "vectorizer.pkl", "rb"))
chunks = [json.loads(l) for l in open(base / "chunks.jsonl", "r", encoding="utf-8")]

q = "validade jurídica e Carimbo do Tempo"
qv = vectorizer.transform([q])
scores = cosine_similarity(qv, X).ravel()
topk = scores.argsort()[::-1][:5]
for idx in topk:
    print(chunks[idx]["id"], scores[idx], chunks[idx]["text"][:160])
```

## Assistants API (Vector Store)
Para usar nos Assistants, você pode simplesmente **subir os PDFs** como Files e anexar a um Vector Store.
Se preferir chunks, suba `chunks.jsonl` com `purpose="assistants"` e use "file_search" no Assistant.
