from beanie import Document
from pydantic import Field

class User(Document):
    name: str
    email: str

    class Settings:
        name = "users"  # ชื่อ collection ใน MongoDB