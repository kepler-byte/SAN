from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime

class UserInDB(BaseModel):
    id: str  # MongoDB _id as string
    username: str
    email: EmailStr
    hashed_password: str
    role: str = "reader"  # reader, creator, admin
    points: int = 0
    settings: Optional[Dict] = {}  # notifications, theme, preferences
    createdAt: datetime
    updatedAt: datetime