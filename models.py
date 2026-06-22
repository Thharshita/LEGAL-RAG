import uuid
from datetime import datetime
from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Integer, Float, TIMESTAMP, ForeignKey, UniqueConstraint, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from config import settings


class Document(Base):
    __tablename__ = "documents"
    doc_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    content_hash: Mapped[str] = mapped_column(String, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, default="application/text")
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    chunks: Mapped[list["DocChunkRegistry"]] = relationship(back_populates="document")


#embedding-->baii
class DocChunkRegistry(Base):
    __tablename__ = "doc_chunk_registry"
    __table_args__ = (UniqueConstraint('doc_id', 'chunk_index', 'doc_version', 'index_version'),)

    chunk_vector_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.doc_id"))
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content_hash: Mapped[str] = mapped_column(String, nullable=False)
    chunk_text: Mapped[str] = mapped_column(String, nullable=False)
    section_heading: Mapped[str | None] = mapped_column(String, nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedding = mapped_column(Vector(settings.embedding_dim), nullable=True)
    doc_version: Mapped[int] = mapped_column(Integer, default=1)           
    index_version: Mapped[str] = mapped_column(String, nullable=False)    
    embedding_model: Mapped[str | None] = mapped_column(String, nullable=True)   
    embedding_dim: Mapped[int | None] = mapped_column(Integer, nullable=True)    
    status: Mapped[str] = mapped_column(String, default="active") 
    valid_from: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    indexed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    document: Mapped["Document"] = relationship(back_populates="chunks")


# 3---------------------
class IndexAlias(Base): #when u create new index for 
    __tablename__ = "index_alias"

    alias_name: Mapped[str] = mapped_column(String, primary_key=True)
    index_version: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str]=mapped_column(String)
    started_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    docs_indexed: Mapped[int] = mapped_column(Integer, default=0)
    docs_same:Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="running")  # running | success | failed


class RetrievalTrace(Base):
    __tablename__ = "retrieval_traces"

    trace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_text: Mapped[str] = mapped_column(String, nullable=False)
    index_version: Mapped[str] = mapped_column(String, nullable=False)
    embedding_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    retrieval_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rerank_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    llm_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunks_retrieved: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    faithfulness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())



# from sqlalchemy import Index

# Index(
#     "idx_chunk_doc_active",
#     DocChunkRegistry.doc_id,
#     postgresql_where=(DocChunkRegistry.status == "active")
# )

# Index(
#     "idx_chunk_bm25_text",
#     func.to_tsvector('english', DocChunkRegistry.chunk_text),
#     postgresql_using="gin"
# )