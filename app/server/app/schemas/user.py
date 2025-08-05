from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str