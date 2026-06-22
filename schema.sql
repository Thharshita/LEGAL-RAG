
-- CREATE EXTENSION IF NOT EXISTS vector;
-- CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- for gen_random_uuid()


-- CREATE INDEX idx_chunk_doc_active ON doc_chunk_registry (doc_id) WHERE status = 'active';
-- CREATE INDEX idx_chunk_embedding ON doc_chunk_registry USING hnsw (embedding vector_cosine_ops) WHERE status = 'active';
-- CREATE INDEX idx_chunk_bm25_text ON doc_chunk_registry USING gin (to_tsvector('english', chunk_text));
