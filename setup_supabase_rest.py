"""
Setup do Supabase via API REST
Cria as tabelas usando SQL via API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://nywykslatlripxpiehfb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

def execute_sql(sql_query):
    """Executa SQL via API REST do Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {"query": sql_query}
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    return response

def create_tables_via_api():
    """Cria tabelas usando a API do Supabase"""
    print("\n[*] Criando tabelas via API REST do Supabase...")
    
    # SQL para criar as tabelas
    sql_commands = [
        # Habilitar extensão pgvector
        "CREATE EXTENSION IF NOT EXISTS vector;",
        
        # Tabela aria_chunks
        """
        CREATE TABLE IF NOT EXISTS aria_chunks (
            id BIGSERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            embedding vector(1536),
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Tabela aria_sessions
        """
        CREATE TABLE IF NOT EXISTS aria_sessions (
            id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255),
            channel VARCHAR(50) DEFAULT 'web',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata JSONB DEFAULT '{}'
        );
        """,
        
        # Tabela aria_messages
        """
        CREATE TABLE IF NOT EXISTS aria_messages (
            id BIGSERIAL PRIMARY KEY,
            session_id VARCHAR(255) REFERENCES aria_sessions(id) ON DELETE CASCADE,
            role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata JSONB DEFAULT '{}'
        );
        """,
    ]
    
    for i, sql in enumerate(sql_commands, 1):
        print(f"[*] Executando comando {i}/{len(sql_commands)}...")
        try:
            # Como não temos a função exec_sql, vamos usar outro método
            # Vamos criar um script SQL e instruir o usuário
            pass
        except Exception as e:
            print(f"[AVISO] Erro: {e}")
    
    print("\n[INFO] Para criar as tabelas, use o SQL Editor do Supabase:")
    print("https://supabase.com/dashboard/project/nywykslatlripxpiehfb/editor/sql")
    print("\nCopie e cole o conteúdo do arquivo: supabase_schema.sql")

def verify_tables():
    """Verifica se as tabelas existem via API REST"""
    print("\n[*] Verificando tabelas existentes...")
    
    url = f"{SUPABASE_URL}/rest/v1/aria_chunks"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    
    try:
        response = requests.get(f"{url}?select=id&limit=1", headers=headers, timeout=10)
        if response.status_code == 200:
            print("[OK] Tabela aria_chunks existe!")
            return True
        elif response.status_code == 404:
            print("[AVISO] Tabela aria_chunks não encontrada")
            return False
        else:
            print(f"[AVISO] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERRO] Erro ao verificar: {e}")
        return False

def test_rag_endpoint():
    """Testa o endpoint RAG local"""
    print("\n[*] Testando endpoint RAG local...")
    
    url = "http://localhost:7777/rag/query"
    headers = {
        "Authorization": "Bearer dtransforma2026",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": "teste",
        "k": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            print("[OK] Endpoint RAG funcionando!")
            return True
        else:
            print(f"[AVISO] Status: {response.status_code}")
            print(f"[INFO] Resposta: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[AVISO] Erro ao testar: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("   ARIA-SDR - Setup Supabase via REST API")
    print("=" * 60)
    
    if not SUPABASE_KEY:
        print("[ERRO] SUPABASE_SERVICE_ROLE_KEY não configurada")
        exit(1)
    
    print(f"\n[INFO] Supabase URL: {SUPABASE_URL}")
    print(f"[INFO] Service Role Key: {SUPABASE_KEY[:20]}...")
    
    # Verificar se as tabelas já existem
    tables_exist = verify_tables()
    
    if not tables_exist:
        print("\n[INFO] Tabelas não encontradas. Você precisa criá-las manualmente:")
        print("\n1. Acesse o SQL Editor do Supabase:")
        print("   https://supabase.com/dashboard/project/nywykslatlripxpiehfb/editor/sql")
        print("\n2. Copie o conteúdo do arquivo: supabase_schema.sql")
        print("\n3. Cole no SQL Editor e clique em 'Run'")
        print("\n4. Execute este script novamente para verificar")
    else:
        print("\n[OK] Tabelas já existem!")
    
    # Testar endpoint RAG
    test_rag_endpoint()
    
    print("\n[INFO] Setup concluído!")
    print("\nPróximos passos:")
    print("1. Certifique-se de que as tabelas existem (use SQL Editor)")
    print("2. Reinicie o servidor: python main.py")
    print("3. Teste o RAG via frontend: http://localhost:3000")

