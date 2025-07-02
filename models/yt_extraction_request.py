from pydantic import BaseModel
from typing import Optional

class SocialInfo(BaseModel):
    include: bool
    count: int

class YTExtractionRequest(BaseModel):
    link: str
    title: str
    blog: bool = True
    linked_in: Optional[SocialInfo] = None
    twitter: Optional[SocialInfo] = None
    facebook: Optional[SocialInfo] = None
    reddit: Optional[SocialInfo] = None
    blog: bool = True