from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserModel(Document):
    name: str
    email: str
    password_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    async def set_password(self, plain_password: str):
        self.password_hash = pwd_context.hash(plain_password)

    async def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password_hash)

    class Settings:
        name = "users"
