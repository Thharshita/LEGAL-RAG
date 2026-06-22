from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.ingestion import get_current_index_version,process_s3_document
from models import IngestionRun
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

@router.post("/ingest")
async def ingest_document(bucket: str, key: str, db: AsyncSession = Depends(get_db)):
    # Start a run
    run = IngestionRun(
        run_id=uuid4(),
        started_at=datetime.utcnow(),
        status="running",
        file_path=f"{bucket}/{key}" 
    )
    db.add(run)
    await db.flush()

    try:
        index_version = await get_current_index_version(db)
        result = await process_s3_document(
            db=db,
            bucket=bucket,
            key=key,
            index_version=index_version
        )
        # Update run stats
        if result["status"]=="skipped":
            run.status="success"
            run.finished_at = datetime.utcnow()
            run.docs_indexed=0
            run.docs_same=result["exists"]

        elif result["status"]=="success":
            run.status="success"
            run.finished_at = datetime.utcnow()
            run.docs_indexed=result["embedded"]
            run.docs_same=result["carry_forward"]
    

        await db.commit()
        return {
            "message":run.status,
            "process_time":run.finished_at
        }
    except Exception as e:
        run.status = "failed"
        run.finished_at = datetime.utcnow()
        await db.commit()
        raise e