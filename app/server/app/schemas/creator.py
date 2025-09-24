from pydantic import BaseModel
from typing import List, Dict

class CreatorBase(BaseModel):
    creatorId: str
    bio: str
    books: List[str] = []
    earnings: float = 0.0
    analytics: Optional[Dict] = {}  # sales, reads etc.