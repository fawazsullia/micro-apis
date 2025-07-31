from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SocialPost:
    content: str
    hashtags: List[str] = field(default_factory=list)
    tone: Optional[str] = None
    title: Optional[str] = None


@dataclass
class SocialPostResponse:
    posts: List[SocialPost]
    count: int
