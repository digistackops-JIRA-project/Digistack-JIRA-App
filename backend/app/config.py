import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "adminuser")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "adminpass")
    DB_NAME: str = os.getenv("DB_NAME", "admindb")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-secret-key-256bit")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_VERSION: str = "1.0.0"
    APP_NAME: str = "SapSecOps Admin Portal"

    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:80")

    class Config:
        env_file = ".env"

settings = Settings()
