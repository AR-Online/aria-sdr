import requests
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im55d3lrc2xhdGxyaXB4cGllaGZiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzE5NjYyMSwiZXhwIjoyMDcyNzcyNjIxfQ.RCZsK_fizrwb-om-unYFCpsDV0sQ43FXWtAvnyIZlF4",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

data = [
    {
        "source": "faq",
        "doc_id": "faq_v1",
        "chunk_index": 0,
        "content": "Como funciona a AR Online...",
        "metadata": {"lang": "pt-BR"},
        "embedding": [0.0123, -0.0045, 0.2234, ...]  # vetor gerado pelo OpenAI
    }
]

resp = requests.post(
    f"https://nywykslatlripxpiehfb.supabase.co/rest/v1/aria_chunks",
    headers=headers,
    json=data
)

print(resp.status_code, resp.json())

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

texto = "Como funciona a AR Online..."
embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input=texto
).data[0].embedding
