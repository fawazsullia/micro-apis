from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any

class BlogData(BaseModel):
    title: str
    sections: List[Any]

class BlogModel(Document):
    contentId: str
    data: BlogData
    job_id: Optional[str] = None
    is_active: bool = True
    tags: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "blogs"
