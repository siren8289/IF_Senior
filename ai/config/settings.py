from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 서버 설정
    DEBUG: bool = True
    SERVICE_NAME: str = "ml-service"

    # 모델 경로
    HEALTH_MODEL_PATH: str = "models/health_model.pkl"
    HEALTH_VECTORIZER_PATH: str = "models/health_vectorizer.pkl"

    # Backend API
    BACKEND_URL: str = "http://localhost:8080"
    BACKEND_API_KEY: Optional[str] = None

    # 로깅
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
