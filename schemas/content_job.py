from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any
from enums import JobStatus, JobContext

class ContentJob(Document):
    content_id: str
    status: JobStatus
    context: JobContext
    completed: bool = False
    token_used: Optional[int] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None # Additional metadata for the job like what was done etc
    tags: Optional[List[str]] = None
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings:
        name = "content_jobs"
