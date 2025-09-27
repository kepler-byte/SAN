from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import certifi
import logging
import asyncio
from app.config import MONGO_URI

# Setup logging
logger = logging.getLogger(__name__)

# MongoDB client with comprehensive SSL configuration
client = AsyncIOMotorClient(
    MONGO_URI,
    # SSL Configuration
    tls=True,
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=False,  # ใน production ควรเป็น False
    tlsAllowInvalidHostnames=False,     # ใน production ควรเป็น False
    
    # Server API
    server_api=ServerApi('1'),
    
    # Connection timeouts
    connectTimeoutMS=30000,
    socketTimeoutMS=30000,
    serverSelectionTimeoutMS=30000,
    maxPoolSize=10,
    minPoolSize=1,
    
    # Retry configuration
    retryWrites=True,
    retryReads=True,
    
    # Heartbeat
    heartbeatFrequencyMS=10000,
)

# Database and collections
database = client.fastapi_jwt_db
user_collection = database.get_collection("users")
book_collection = database.get_collection("book")

async def test_connection():
    """ทดสอบการเชื่อมต่อ MongoDB"""
    try:
        # ทดสอบการ ping
        await client.admin.command('ping')
        logger.info("✓ MongoDB connection successful")
        
        # ทดสอบ database operations
        await user_collection.count_documents({})
        logger.info("✓ Database operations working")
        
        return True
    except Exception as e:
        logger.error(f"✗ MongoDB connection failed: {e}")
        return False

async def get_database_info():
    """ดึงข้อมูล database สำหรับ debugging"""
    try:
        # Server info
        server_info = await client.server_info()
        
        # Database stats
        db_stats = await database.command("dbStats")
        
        # Collections info
        collections = await database.list_collection_names()
        
        return {
            "server_version": server_info.get("version"),
            "database_name": database.name,
            "collections": collections,
            "database_size": db_stats.get("dataSize", 0)
        }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return None

# Connection event handlers
async def on_connection_established():
    """Called when connection is established"""
    logger.info("MongoDB connection established")
    info = await get_database_info()
    if info:
        logger.info(f"Connected to MongoDB {info['server_version']}")
        logger.info(f"Database: {info['database_name']}")
        logger.info(f"Collections: {info['collections']}")

async def ensure_indexes():
    """สร้าง indexes ที่จำเป็น"""
    try:
        # User collection indexes
        await user_collection.create_index("username", unique=True)
        await user_collection.create_index("email", unique=True)
        
        # Book collection indexes (ถ้าต้องการ)
        await book_collection.create_index("title")
        await book_collection.create_index("author")
        
        logger.info("✓ Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Index creation warning: {e}")

# Graceful shutdown
async def close_connection():
    """ปิดการเชื่อมต่อ MongoDB"""
    try:
        client.close()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")

# Alternative configuration for local development
# Uncomment this section for local development without SSL

# For local Connection (MongoDB without SSL)
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
database = client.fastapi_jwt_db
user_collection = database.get_collection("users")
book_collection = database.get_collection("book")

async def test_connection():
    try:
        await client.admin.command('ping')
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False
"""