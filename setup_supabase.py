"""
Script para configurar o banco de dados Supabase
Cria as tabelas necessárias para o ARIA-SDR
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Configurações do Supabase
SUPABASE_CONFIG = {
    "host": os.getenv("SUPABASE_HOST", "db.nywykslatlripxpiehfb.supabase.co"),
    "port": os.getenv("SUPABASE_PORT", "5432"),
    "database": os.getenv("SUPABASE_DATABASE", "postgres"),
    "user": os.getenv("SUPABASE_USER", "postgres"),
    "password": os.getenv("SUPABASE_PASSWORD", "")
}

def test_connection():
    """Testa conexão com o Supabase"""
    try:
        print("[*] Testando conexao com Supabase...")
        conn = psycopg2.connect(**SUPABASE_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print("[OK] Conexao bem-sucedida!")
        print(f"[INFO] PostgreSQL version: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERRO] Erro na conexao: {e}")
        return False

def create_tables():
    """Cria as tabelas necessárias"""
    try:
        print("\n[*] Criando tabelas...")
        conn = psycopg2.connect(**SUPABASE_CONFIG)
        cursor = conn.cursor()
        
        # Tabela para chunks de conhecimento (RAG)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aria_chunks (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector(1536),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        print("[OK] Tabela aria_chunks criada")
        
        # Tabela para sessões/conversas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aria_sessions (
                id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255),
                channel VARCHAR(50),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                metadata JSONB
            );
        """)
        print("[OK] Tabela aria_sessions criada")
        
        # Tabela para mensagens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aria_messages (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) REFERENCES aria_sessions(id),
                role VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                metadata JSONB
            );
        """)
        print("[OK] Tabela aria_messages criada")
        
        # Criar índice para busca vetorial (se extensão pgvector estiver instalada)
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS aria_chunks_embedding_idx 
                ON aria_chunks USING ivfflat (embedding vector_cosine_ops);
            """)
            print("[OK] Extensao pgvector e indice criados")
        except Exception as e:
            print(f"[AVISO] Nao foi possivel criar extensao pgvector: {e}")
            print("   (Isso e normal se voce nao tiver permissoes. O sistema funcionara sem RAG)")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n[OK] Banco de dados configurado com sucesso!")
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro ao criar tabelas: {e}")
        return False

def check_tables():
    """Verifica quais tabelas existem"""
    try:
        print("\n[*] Verificando tabelas existentes...")
        conn = psycopg2.connect(**SUPABASE_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'aria_%'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        if tables:
            print("[OK] Tabelas encontradas:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("[AVISO] Nenhuma tabela ARIA encontrada")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERRO] Erro ao verificar tabelas: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("   ARIA-SDR - Configuracao do Supabase")
    print("=" * 60)
    
    if not SUPABASE_CONFIG["password"]:
        print("[ERRO] SUPABASE_PASSWORD nao configurada no .env")
        exit(1)
    
    # Testar conexão
    if not test_connection():
        print("\n[ERRO] Nao foi possivel conectar ao Supabase")
        print("Verifique as credenciais no arquivo .env")
        exit(1)
    
    # Verificar tabelas existentes
    check_tables()
    
    # Criar tabelas
    create_tables()
    
    # Verificar novamente
    check_tables()
    
    print("\n[OK] Setup concluido!")
    print("\n[INFO] Proximos passos:")
    print("   1. Execute o servidor: teste_local.ps1")
    print("   2. Teste a API: http://localhost:8000/docs")
    print("   3. Use a interface: http://localhost:3000")

