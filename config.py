from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:whatever@localhost:5432/personal"
    embedding_model: str = "BAAI/bge-m3"
    embedding_dimensions: int = 1024
    embedding_dim: int = 1024

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    bucket: str = "legal-rag"

    class Config:
        env_file = ".env"


settings = Settings()
