from pydantic import BaseModel
from datetime import datetime

class ReviewBase(BaseModel):
    userId: str
    bookId: str
    rating: int
    comment: str

class ReviewCreate(ReviewBase):
    pass

class ReviewInDB(ReviewBase):
    reviewId: str
    createdAt: datetime