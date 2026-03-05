from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional

@dataclass
class NewsArticle:
    url: str
    title: str
    content: str
    summary: Optional[str] = None
    published: Optional[datetime] = None
    scraped_at: Optional[datetime] = field(default_factory=datetime.now)
    category: Optional[str] = None
    reviewed: bool = False

    def __post_init__(self):
        if not self.url:
            raise ValueError("url cannot be empty")
        if not self.title:
            raise ValueError("title cannot be empty")

    def to_dict(self) -> dict:
        """Converts to a dict suitable for database insertion."""
        return asdict(self)