from pydantic import BaseModel
from datetime import datetime

class Review(BaseModel):
    reviewId: str
    userId: str
    bookId: str
    rating: int
    comment: str
    createdAt: datetime