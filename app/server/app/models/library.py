from pydantic import BaseModel
from typing import List

class LibraryBook(BaseModel):
    bookId: str
    status: str
    lastReadPage: int = 0

class Library(BaseModel):
    userId: str
    books: List[LibraryBook]