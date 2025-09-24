from pydantic import BaseModel
from typing import List, Dict

class LibraryBook(BaseModel):
    bookId: str
    status: str  # purchased, rented, reading, finished
    lastReadPage: int = 0

class Library(BaseModel):
    userId: str
    books: List[LibraryBook] = []