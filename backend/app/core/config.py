from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Radiology Report Structuring API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # AI Provider
    AI_PROVIDER: Optional[str] = None  # "anthropic", "openai", or "ollama" (auto-detect if None)
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    AI_MODEL: str = "claude-sonnet-4-20250514"  # Model name for all providers

    # Ollama settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB in bytes
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: set = {".json"}  # JSON files with array of report texts
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
