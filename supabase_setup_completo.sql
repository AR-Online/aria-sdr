-- ============================================================
-- ARIA-SDR - Setup Completo do Supabase
-- Execute este script no SQL Editor do Supabase
-- ============================================================

-- 1. Habilitar extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Criar tabela aria_chunks
CREATE TABLE IF NOT EXISTS aria_chunks (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    source TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Criar índice para busca vetorial
CREATE INDEX IF NOT EXISTS aria_chunks_embedding_idx 
ON aria_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 4. Criar índice para busca por texto
CREATE INDEX IF NOT EXISTS aria_chunks_content_idx 
ON aria_chunks USING gin(to_tsvector('portuguese', content));

-- 5. Criar índice para source
CREATE INDEX IF NOT EXISTS aria_chunks_source_idx 
ON aria_chunks(source);

-- 6. Criar tabela aria_sessions
CREATE TABLE IF NOT EXISTS aria_sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    channel VARCHAR(50) DEFAULT 'web',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS aria_sessions_user_id_idx ON aria_sessions(user_id);
CREATE INDEX IF NOT EXISTS aria_sessions_channel_idx ON aria_sessions(channel);

-- 7. Criar tabela aria_messages
CREATE TABLE IF NOT EXISTS aria_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES aria_sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS aria_messages_session_id_idx ON aria_messages(session_id);
CREATE INDEX IF NOT EXISTS aria_messages_created_at_idx ON aria_messages(created_at);

-- 8. Criar função RPC para busca vetorial
CREATE OR REPLACE FUNCTION match_aria_chunks(
    query_embedding vector(1536),
    match_count int DEFAULT 5,
    filter_source text DEFAULT NULL
)
RETURNS TABLE (
    id bigint,
    content text,
    metadata jsonb,
    source text,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.content,
        c.metadata,
        c.source,
        1 - (c.embedding <=> query_embedding) as similarity
    FROM aria_chunks c
    WHERE 
        (filter_source IS NULL OR c.source = filter_source)
        AND c.embedding IS NOT NULL
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 9. Inserir dado de teste
INSERT INTO aria_chunks (content, metadata, source) VALUES
(
    'ARIA é um sistema de relacionamento inteligente desenvolvido com o framework Agno. O sistema oferece atendimento automatizado via WhatsApp, classificação de volume de envios e roteamento inteligente.',
    '{"tipo": "info", "categoria": "sobre"}',
    'faq'
)
ON CONFLICT DO NOTHING;

-- 10. Habilitar Row Level Security (RLS)
ALTER TABLE aria_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE aria_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE aria_messages ENABLE ROW LEVEL SECURITY;

-- 11. Criar políticas RLS
DROP POLICY IF EXISTS "Service role has full access to aria_chunks" ON aria_chunks;
CREATE POLICY "Service role has full access to aria_chunks"
    ON aria_chunks FOR ALL
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "Service role has full access to aria_sessions" ON aria_sessions;
CREATE POLICY "Service role has full access to aria_sessions"
    ON aria_sessions FOR ALL
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "Service role has full access to aria_messages" ON aria_messages;
CREATE POLICY "Service role has full access to aria_messages"
    ON aria_messages FOR ALL
    USING (true)
    WITH CHECK (true);

-- 12. Verificação final
SELECT 'Setup concluído! Tabelas criadas:' as status;
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'aria_%'
ORDER BY table_name;

SELECT 'Total de chunks:', COUNT(*) FROM aria_chunks;

