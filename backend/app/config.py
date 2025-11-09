"""
Configuration module for HomeWise AI application
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = "HomeWise AI"
    app_env: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"

    # Property Data APIs
    domain_api_key: str = ""
    realestate_api_key: str = ""
    corelogic_api_key: str = ""

    # Vector Database (Pinecone)
    pinecone_api_key: str = ""
    pinecone_environment: str = "gcp-starter"
    pinecone_index_name: str = "homewise-property-data"

    # Database
    database_url: str = "sqlite:///./homewise.db"
    redis_url: str = "redis://localhost:6379/0"

    # External APIs
    rba_api_base_url: str = "https://www.rba.gov.au/statistics"
    abs_api_base_url: str = "https://api.data.abs.gov.au"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Embedding Model
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 1000
    chunk_overlap: int = 200

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
