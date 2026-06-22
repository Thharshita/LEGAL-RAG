# import asyncio
# from sqlalchemy import text
# from database import engine
# from models import Base

# async def create_tables():
#     async with engine.begin() as conn:
        
#         await conn.execute(text(
#             "CREATE EXTENSION IF NOT EXISTS vector"
#         ))

#         await conn.execute(text(
#             "CREATE EXTENSION IF NOT EXISTS pgcrypto"
#         ))

#         await conn.run_sync(Base.metadata.create_all)

#         await conn.execute(text("""
#             CREATE INDEX IF NOT EXISTS idx_chunk_embedding
#             ON doc_chunk_registry
#             USING hnsw (embedding vector_cosine_ops)
#             WHERE status = 'active'
#         """))
        
#         await conn.execute(text("""
#             INSERT OR IGNORE INTO index_alias (alias_name, index_version) 
#             VALUES ('current', 'v1')
#         """))
#         await conn.commit()
#     print("Database tables created successfully")

# if __name__ == "__main__":
#     asyncio.run(create_tables())