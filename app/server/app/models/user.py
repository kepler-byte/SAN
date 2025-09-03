from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    email: str
    hashed_password: str

class UserInDB(User):
    id: str