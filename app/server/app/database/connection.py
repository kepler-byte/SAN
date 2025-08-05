from motor.motor_asyncio import AsyncIOMotorClient
from ..config import MONGODB_URL, DATABASE_NAME

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

async def connect_to_db():
    # ตรวจสอบการเชื่อมต่อ (ไม่จำเป็น แต่ดี)
    pass

async def close_db_connection():
    client.close()