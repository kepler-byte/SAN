from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI
import logging

# Setup logging
logger = logging.getLogger(__name__)

# MongoDB client with SSL configuration
client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=True,   # For development
    tlsAllowInvalidHostnames=True,      # For development
    server_api=ServerApi('1'),
    connectTimeoutMS=10000,
    socketTimeoutMS=10000,
    serverSelectionTimeoutMS=10000,
    maxPoolSize=10,
    minPoolSize=1,
    retryWrites=True,
    retryReads=True,
    heartbeatFrequencyMS=30000,
)

# Database and collections
database = client.fastapi_jwt_db
user_collection = database.get_collection("users")

book_collection = database.get_collection("book")