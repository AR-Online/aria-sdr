-- ============================================================
-- CORREÇÃO da Função RPC para RAG (Versão 2)
-- Execute este SQL no Supabase
-- ============================================================

-- 1. DELETAR a função antiga
DROP FUNCTION IF EXISTS match_aria_chunks(vector, integer, text);

-- 2. CRIAR a função corrigida
CREATE OR REPLACE FUNCTION match_aria_chunks(
    query_embedding vector(1536),
    match_count int DEFAULT 5,
    filter_source text DEFAULT NULL
)
RETURNS TABLE (
    id bigint,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        aria_chunks.id,
        aria_chunks.content,
        aria_chunks.metadata,
        1 - (aria_chunks.embedding <=> query_embedding) as similarity
    FROM aria_chunks
    WHERE 
        (filter_source IS NULL OR aria_chunks.source = filter_source)
        AND aria_chunks.embedding IS NOT NULL
    ORDER BY aria_chunks.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 3. Verificar que foi criada
SELECT 'Função match_aria_chunks corrigida com sucesso!' as status;

-- 4. Testar se funciona (deve retornar 0 linhas se não houver embeddings)
SELECT * FROM match_aria_chunks(
    (SELECT embedding FROM aria_chunks WHERE embedding IS NOT NULL LIMIT 1),
    1,
    'faq'
);

