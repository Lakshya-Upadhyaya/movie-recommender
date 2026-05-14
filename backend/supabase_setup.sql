-- 1. Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 2. Table
CREATE TABLE IF NOT EXISTS movies (
    id          bigserial PRIMARY KEY,
    title       text,
    description text,
    directed_by text,
    starring    text,
    language    text,
    release_date text,
    all_sentiments jsonb,
    embedding   vector(768)   -- nomic-embed-text-v1.5 output dimension
);

-- 3. Indexes
CREATE UNIQUE INDEX IF NOT EXISTS movies_pkey         ON movies USING btree (id);
CREATE INDEX        IF NOT EXISTS movies_embedding_idx ON movies USING hnsw  (embedding vector_cosine_ops);
CREATE INDEX        IF NOT EXISTS idx_movies_title     ON movies USING gin   (title       gin_trgm_ops);
CREATE INDEX        IF NOT EXISTS idx_movies_starring  ON movies USING gin   (starring    gin_trgm_ops);
CREATE INDEX        IF NOT EXISTS idx_movies_director  ON movies USING gin   (directed_by gin_trgm_ops);
CREATE INDEX        IF NOT EXISTS idx_movies_language  ON movies USING gin   (language    gin_trgm_ops);

-- 4. RPC function
CREATE OR REPLACE FUNCTION match_movies(
    query_embedding  vector,
    match_count      int,
    starring_filter  text    DEFAULT NULL,
    director_filter  text    DEFAULT NULL,
    title_filter     text    DEFAULT NULL,
    year_filter      int     DEFAULT NULL,
    language_filter  text    DEFAULT NULL
)
RETURNS TABLE (
    id             bigint,
    title          text,
    description    text,
    directed_by    text,
    starring       text,
    all_sentiments jsonb,
    release_date   text
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.title,
        m.description,
        m.directed_by,
        m.starring,
        m.all_sentiments,
        m.release_date
    FROM movies m
    WHERE
        (starring_filter  IS NULL OR m.starring    ILIKE '%' || starring_filter  || '%')
        AND (director_filter  IS NULL OR m.directed_by ILIKE '%' || director_filter  || '%')
        AND (title_filter     IS NULL OR m.title       ILIKE '%' || title_filter     || '%')
        AND (language_filter  IS NULL OR m.language    ILIKE '%' || language_filter  || '%')
        AND (year_filter      IS NULL OR (
                m.release_date ~ '^\d{2}-\d{2}-\d{4}$'
                AND EXTRACT(YEAR FROM TO_DATE(m.release_date, 'DD-MM-YYYY')) = year_filter
            ))
    ORDER BY m.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;