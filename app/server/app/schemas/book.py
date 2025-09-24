from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = ""
    price: int
    coverImage: Optional[str] = None
    filePath: str
    category: Optional[str] = "novel"
    rating: Optional[float] = 0.0
    reviews: Optional[List[str]] = []
    createdBy: str  # userId

class BookCreate(BookBase):
    pass

class BookInDB(BookBase):
    bookId: str
    createdAt: datetime
    updatedAt: datetime

class BookResponse(BookBase):
    bookId: str