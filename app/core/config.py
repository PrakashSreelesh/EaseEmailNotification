from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # SuperUser
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

    # Email
    EMAIL_BACKEND: str
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USE_TLS: bool
    EMAIL_HOST_USER: Optional[str] = None
    EMAIL_HOST_PASSWORD: Optional[str] = None
    DEFAULT_FROM_EMAIL: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
            self.CELERY_RESULT_BACKEND = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
