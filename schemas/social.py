from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any

class SocialData(BaseModel):
    title: str
    sections: List[Any]

class SocialModal(Document):
    contentId: str
    data: SocialData
    is_active: bool = True
    tags: Optional[List[str]] = None
    type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "socials"
