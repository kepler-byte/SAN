from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Book(BaseModel):
    bookId: str
    title: str
    author: str
    description: Optional[str]
    price: int
    coverImage: Optional[str]
    filePath: str
    category: Optional[str]
    rating: float = 0.0
    reviews: List[str] = []
    createdBy: str
    createdAt: datetime
    updatedAt: datetime