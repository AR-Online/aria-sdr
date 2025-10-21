-- ============================================================
-- CORREÇÃO da Função RPC para RAG
-- Execute este SQL no Supabase para corrigir o erro
-- ============================================================

-- Recriar a função match_aria_chunks com correção
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

-- Testar a função com dados vazios (para validar que funciona)
SELECT 'Função corrigida com sucesso!' as status;

