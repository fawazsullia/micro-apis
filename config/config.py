from typing import Optional

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
import models as models
import os


class Settings(BaseSettings):
    # database configurations
    MONGO_URI: str = os.getenv("DATABASE_URL", "mongodb://localhost:27017/micro_apis")

    # JWT
    secret_key: str = "secret"
    algorithm: str = "HS256"
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "sds")
    YT_GOOGLE_API_KEY: str = os.getenv("YT_GOOGLE_API_KEY", "your-youtube-api-key")

    class Config:
        env_file = ".env"
        from_attributes = True
        extra = "allow"

settings = Settings()
