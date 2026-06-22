from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession
from ..my_logger import logger
from ..text_model import S3_bucket   # import the class
import fitz
import hashlib
from models import Document, DocChunkRegistry, IngestionRun
from sqlalchemy import select, update
from data_processing.text_processing import text_splitter
from data_processing.embedding_model import embedding_obj
from uuid import uuid4
from datetime import datetime

# Instantiate S3 client once (or inside function)
s3_client = S3_bucket().bucket()

async def get_current_index_version(db: AsyncSession) -> str:
    row = (await db.execute(
        sql_text("SELECT index_version FROM index_alias WHERE alias_name = 'current'")
    )).first()
    if row is None:
        raise ValueError("No 'current' index alias found")
    logger.info(f"get index version:{row[0]}")
    return row[0]

def download_pdf_from_s3(bucket: str, key: str) -> bytes:
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()

def extract_pdf_pages(pdf_bytes: bytes) -> list[tuple[int, str]]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return [(i + 1, page.get_text()) for i, page in enumerate(doc)]

def extract_text(text_bytes: bytes) -> list[tuple[int, str]]:
    text = text_bytes.decode("utf-8")
    return [(1, text)]

def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

async def process_s3_document(db: AsyncSession, bucket: str, key: str, index_version: str):
    # 1. Download and parse
    file_bytes = download_pdf_from_s3(bucket, key)
    if key.endswith(".pdf"):
        pages = extract_pdf_pages(file_bytes)
    elif key.endswith(".txt"):
        pages = extract_text(file_bytes)
    else:
        raise ValueError("Unsupported file type")

    full_text = "\n".join(text for _, text in pages)
    file_hash = compute_hash(full_text)

    # 2. Check existing document
    stmt = select(Document).where(Document.file_path == key)
    existing = (await db.execute(stmt)).scalar_one_or_none()

    if existing and existing.content_hash == file_hash:
        return {"status": "skipped", "reason": "document unchanged","exists":len(pages)}

    # 3. Create or update Document
    if existing:
        existing.content_hash = file_hash
        existing.version += 1
        doc = existing
    else:
        doc = Document(
            doc_id=uuid4(),
            file_name=key,
            file_path=key,
            content_hash=file_hash,
            mime_type="application/pdf" if key.endswith(".pdf") else "text/plain",
            version=1
        )
        db.add(doc)
        await db.flush()   # get doc.doc_id

    # 4. Index document chunks
    result = await index_document(
        db=db,
        doc=doc,
        pages=pages,
        index_version=index_version
    )

    await db.commit()
    return {
        "status": "success",
        "document": key,
        "embedded": result["embedded"],
        "carried_forward": result["carried_forward"]
    }

async def index_document(db: AsyncSession, doc: Document, pages: list[tuple[int, str]], index_version: str):
    logger.info(f"index version: {index_version}")

    all_text = "\n".join(text for _, text in pages)
    new_chunks = text_splitter(all_text)   


    stmt = select(DocChunkRegistry).where(
        DocChunkRegistry.doc_id == doc.doc_id,
        DocChunkRegistry.status == "active"
    )
    result = await db.execute(stmt) ##result=[] if no same file existed
    old_chunks = result.scalars().all()
    old_by_index = {c.chunk_index: c for c in old_chunks}

    to_embed = []      # (idx, chunk_text, hash)
    carry_forward = [] # (idx, old_row)

    for idx, chunk_text in enumerate(new_chunks):
        c_hash = compute_hash(chunk_text)
        old = old_by_index.get(idx)
        logger.info(f"old hash of chuck with same index:{old}")
        if old is not None and old.content_hash == c_hash:
            carry_forward.append((idx, old))
        else:
            to_embed.append((idx, chunk_text, c_hash))
    
    logger.info(f"carry_forward:{carry_forward}, to_embed:{to_embed}")
    # Supersede all currently active chunks for this doc
    await db.execute(
        update(DocChunkRegistry)
        .where(DocChunkRegistry.doc_id == doc.doc_id, DocChunkRegistry.status == "active")
        .values(status="superseded")
    )

    # Compute embeddings for new/changed chunks
    embeddings = embedding_obj.create_embeddings([c for _, c, _ in to_embed]) if to_embed else []

    # Carry forward unchanged chunks (new rows with same embedding, new index_version)
    for idx, old in carry_forward:
        db.add(DocChunkRegistry(
            doc_id=doc.doc_id,
            chunk_index=idx,
            content_hash=old.content_hash,
            chunk_text=old.chunk_text,
            section_heading=old.section_heading,
            page_number=old.page_number,
            embedding=old.embedding,
            doc_version=doc.version,          # current document version
            index_version=index_version,      # new index version
            embedding_model=old.embedding_model,  # copy from old
            embedding_dim=old.embedding_dim,
            status="active"
        ))

    # Insert new/changed chunks with fresh embeddings
    for (idx, chunk_text, c_hash), emb in zip(to_embed, embeddings):
        db.add(DocChunkRegistry(
            doc_id=doc.doc_id,
            chunk_index=idx,
            content_hash=c_hash,
            chunk_text=chunk_text,
            section_heading=None,      # you can extract from page metadata if needed
            page_number=1,             # or from pages list
            embedding=emb.tolist(),
            doc_version=doc.version,
            index_version=index_version,
            embedding_model=embedding_obj.model_name,
            embedding_dim=len(emb),
            status="active"
        ))

    return {"embedded": len(to_embed), "carried_forward": len(carry_forward)}