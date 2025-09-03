from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
database = client.fastapi_jwt_db
user_collection = database.get_collection("users")