from pydantic import BaseModel, EmailStr
from typing import Optional, Dict

# ใช้เหมือนเดิมสำหรับ Auth
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Optional: สำหรับ Response ข้อมูลผู้ใช้โดยไม่เปิดเผย password
class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str = "reader"
    points: int = 0
    settings: Optional[Dict] = {}