from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Firebase
    FIREBASE_PROJECT_ID: str
    FIREBASE_API_KEY: str
    FIREBASE_AUTH_DOMAIN: str
    FIREBASE_SERVICE_ACCOUNT: str
    # n8n
    N8N_WEBHOOK_URL: str
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "n8n Bot Hub Backend"
    DEBUG: bool = False
    
    # Evolution API
    EVOLUTION_API_URL: str
    EVOLUTION_API_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
