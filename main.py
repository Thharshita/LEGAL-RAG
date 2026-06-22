from fastapi import FastAPI
from .routers import ingestion
from database import engine
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan,title="RAG Production Pipeline")

app.include_router(ingestion.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
