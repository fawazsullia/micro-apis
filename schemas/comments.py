from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any
from .blog import BlogModel
from .social import SocialModal

class Comment(BaseModel):
    text: str
    name: str

class CommentModel(Document):
    contentId: str
    comments: List[Comment] = Field(default_factory=list)
    is_active: bool = True
    job_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings:
        name = "comments"
