from pydantic import BaseModel
from typing import List, Dict

class Creator(BaseModel):
    creatorId: str
    bio: str
    books: List[str]
    earnings: float
    analytics: Dict