from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any
from .blog import BlogModel
from .social import SocialModal

class ContentModel(Document):
    title: str
    userId: str
    blogs: List[BlogModel] = Field(default_factory=list)
    raw_text: Optional[str] = None
    video_title: Optional[str] = None
    video_description: Optional[str] = None
    link: str
    tags: Optional[List[str]] = None
    is_active: bool = True
    socials: List[SocialModal] = Field(default_factory=list)
    ideas_from_comments: Optional[List[str]] = None
    sentiment: Optional[Any] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings:
        name = "contents"
