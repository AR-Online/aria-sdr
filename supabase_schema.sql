-- ============================================================
-- ARIA-SDR - Schema do Banco de Dados Supabase
-- ============================================================
-- Execute este script no SQL Editor do Supabase:
-- https://supabase.com/dashboard/project/nywykslatlripxpiehfb/editor/sql
-- ============================================================

-- Habilitar extensão pgvector para embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela para chunks de conhecimento (RAG/Embeddings)
CREATE TABLE IF NOT EXISTS aria_chunks (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca vetorial híbrida
CREATE INDEX IF NOT EXISTS aria_chunks_embedding_idx 
ON aria_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Índice para busca por texto
CREATE INDEX IF NOT EXISTS aria_chunks_content_idx 
ON aria_chunks USING gin(to_tsvector('portuguese', content));

-- Tabela para sessões/conversas
CREATE TABLE IF NOT EXISTS aria_sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    channel VARCHAR(50) DEFAULT 'web',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Índice para buscar sessões por usuário
CREATE INDEX IF NOT EXISTS aria_sessions_user_id_idx 
ON aria_sessions(user_id);

-- Índice para buscar sessões por canal
CREATE INDEX IF NOT EXISTS aria_sessions_channel_idx 
ON aria_sessions(channel);

-- Tabela para mensagens
CREATE TABLE IF NOT EXISTS aria_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES aria_sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Índice para buscar mensagens por sessão
CREATE INDEX IF NOT EXISTS aria_messages_session_id_idx 
ON aria_messages(session_id);

-- Índice para ordenar mensagens por data
CREATE INDEX IF NOT EXISTS aria_messages_created_at_idx 
ON aria_messages(created_at);

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para atualizar updated_at em aria_sessions
CREATE TRIGGER update_aria_sessions_updated_at 
    BEFORE UPDATE ON aria_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para atualizar updated_at em aria_chunks
CREATE TRIGGER update_aria_chunks_updated_at 
    BEFORE UPDATE ON aria_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Habilitar Row Level Security (RLS)
ALTER TABLE aria_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE aria_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE aria_messages ENABLE ROW LEVEL SECURITY;

-- Política para permitir acesso com service_role
CREATE POLICY "Service role has full access to aria_chunks"
    ON aria_chunks FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to aria_sessions"
    ON aria_sessions FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to aria_messages"
    ON aria_messages FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================================
-- Dados de teste (opcional - pode comentar se não quiser)
-- ============================================================

-- Inserir chunk de exemplo
INSERT INTO aria_chunks (content, metadata) VALUES
(
    'A AR Online é uma empresa especializada em Apostilas Eletrônicas de Registro (AER) e soluções digitais para cartórios.',
    '{"source": "about", "type": "info"}'
)
ON CONFLICT DO NOTHING;

-- ============================================================
-- Verificação
-- ============================================================

-- Listar todas as tabelas criadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'aria_%'
ORDER BY table_name;

-- Contar registros
SELECT 
    'aria_chunks' as tabela, COUNT(*) as total FROM aria_chunks
UNION ALL
SELECT 'aria_sessions' as tabela, COUNT(*) as total FROM aria_sessions
UNION ALL
SELECT 'aria_messages' as tabela, COUNT(*) as total FROM aria_messages;

