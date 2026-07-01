from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Bot Configuration
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    BOT_NAME: str = Field("Annopow Support Bot", env="BOT_NAME")
    ADMIN_IDS: List[int] = Field(default_factory=list, env="ADMIN_IDS")
    
    # Database
    DATABASE_URL: str = Field(
        "postgresql://postgres:password@localhost:5432/annopow_db", 
        env="DATABASE_URL"
    )
    
    # Redis
    REDIS_URL: Optional[str] = Field(None, env="REDIS_URL")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field("gpt-3.5-turbo", env="OPENAI_MODEL")
    ENABLE_AI: bool = Field(False, env="ENABLE_AI")
    
    # Application
    DEBUG: bool = Field(False, env="DEBUG")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    
    # Mode Settings
    DEFAULT_MODE: str = Field("auto", env="DEFAULT_MODE")
    AUTO_REPLY_ENABLED: bool = Field(True, env="AUTO_REPLY_ENABLED")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(30, env="RATE_LIMIT_PER_MINUTE")
    
    # Languages
    DEFAULT_LANGUAGE: str = Field("en", env="DEFAULT_LANGUAGE")
    
    # Railway specific
    PORT: int = Field(8080, env="PORT")
    RAILWAY_ENVIRONMENT: bool = Field(False, env="RAILWAY_ENVIRONMENT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()

# Parse ADMIN_IDS from string if needed
if isinstance(settings.ADMIN_IDS, str):
    settings.ADMIN_IDS = [int(x.strip()) for x in settings.ADMIN_IDS.split(',') if x.strip()]
