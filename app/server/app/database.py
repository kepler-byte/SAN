from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from pymongo.server_api import ServerApi
import certifi
import logging
import asyncio
from app.config import MONGO_URI

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
book_collection = database.get_collection("books")  # Changed from "book" to "books"

# GridFS buckets for file storage
pdf_gridfs_bucket = AsyncIOMotorGridFSBucket(database, bucket_name="pdfs")
cover_gridfs_bucket = AsyncIOMotorGridFSBucket(database, bucket_name="covers")

async def test_connection():
    """ทดสอบการเชื่อมต่อ MongoDB"""
    try:
        await asyncio.wait_for(
            client.admin.command('ping'), 
            timeout=10.0
        )
        logger.info("✓ MongoDB connection successful")
        
        # Test basic operations
        await asyncio.wait_for(
            user_collection.count_documents({}),
            timeout=5.0
        )
        logger.info("✓ Database operations working")
        
        # Test GridFS buckets
        await test_gridfs_buckets()
        
        return True
    except asyncio.TimeoutError:
        logger.error("✗ MongoDB connection timeout")
        return False
    except Exception as e:
        logger.error(f"✗ MongoDB connection failed: {e}")
        return False

async def test_gridfs_buckets():
    """Test GridFS buckets functionality"""
    try:
        # Test if we can access GridFS buckets
        pdf_files = await pdf_gridfs_bucket.find().to_list(length=1)
        cover_files = await cover_gridfs_bucket.find().to_list(length=1)
        
        logger.info("✓ GridFS buckets accessible")
        logger.info(f"  - PDF files in GridFS: {len(pdf_files) if pdf_files else 0}")
        logger.info(f"  - Cover files in GridFS: {len(cover_files) if cover_files else 0}")
        
    except Exception as e:
        logger.warning(f"GridFS bucket test failed: {e}")

async def get_database_info():
    """ดึงข้อมูล database สำหรับ debugging"""
    try:
        server_info = await asyncio.wait_for(
            client.server_info(),
            timeout=5.0
        )
        
        db_stats = await asyncio.wait_for(
            database.command("dbStats"),
            timeout=5.0
        )
        
        collections = await asyncio.wait_for(
            database.list_collection_names(),
            timeout=5.0
        )
        
        # Get GridFS collection info
        gridfs_collections = [col for col in collections if col.endswith('.files') or col.endswith('.chunks')]
        
        return {
            "server_version": server_info.get("version"),
            "database_name": database.name,
            "collections": collections,
            "gridfs_collections": gridfs_collections,
            "database_size": db_stats.get("dataSize", 0),
            "storage_size": db_stats.get("storageSize", 0)
        }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return None

async def ensure_indexes():
    """สร้าง indexes ที่จำเป็น"""
    try:
        if not await test_connection():
            logger.warning("Skipping index creation - no database connection")
            return
            
        # User collection indexes
        await user_collection.create_index("username", unique=True)
        await user_collection.create_index("email", unique=True)
        
        # Book collection indexes
        await book_collection.create_index("title")
        await book_collection.create_index("author")
        await book_collection.create_index("category")
        await book_collection.create_index("created_at")
        await book_collection.create_index("rating")
        
        # GridFS indexes are automatically created by MongoDB
        # But we can create additional indexes for better performance
        await database.get_collection("pdfs.files").create_index("metadata.file_type")
        await database.get_collection("covers.files").create_index("metadata.file_type")
        
        logger.info("✓ Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Index creation warning: {e}")

async def cleanup_orphaned_files():
    """Clean up GridFS files that don't have corresponding book records"""
    try:
        # Get all PDF file IDs from GridFS
        pdf_files = await pdf_gridfs_bucket.find().to_list(length=None)
        pdf_file_ids = [file._id for file in pdf_files]
        
        # Get all cover file IDs from GridFS
        cover_files = await cover_gridfs_bucket.find().to_list(length=None)
        cover_file_ids = [file._id for file in cover_files]
        
        # Get all book records
        books = await book_collection.find({}, {"pdf_id": 1, "cover_id": 1}).to_list(length=None)
        
        # Extract referenced file IDs from books
        referenced_pdf_ids = set()
        referenced_cover_ids = set()
        
        for book in books:
            if book.get("pdf_id"):
                referenced_pdf_ids.add(book["pdf_id"])
            if book.get("cover_id"):
                referenced_cover_ids.add(book["cover_id"])
        
        # Find orphaned files
        orphaned_pdfs = set(pdf_file_ids) - referenced_pdf_ids
        orphaned_covers = set(cover_file_ids) - referenced_cover_ids
        
        # Delete orphaned files
        deleted_pdfs = 0
        deleted_covers = 0
        
        for pdf_id in orphaned_pdfs:
            await pdf_gridfs_bucket.delete(pdf_id)
            deleted_pdfs += 1
        
        for cover_id in orphaned_covers:
            await cover_gridfs_bucket.delete(cover_id)
            deleted_covers += 1
        
        if deleted_pdfs > 0 or deleted_covers > 0:
            logger.info(f"✓ Cleanup completed: {deleted_pdfs} PDFs, {deleted_covers} covers deleted")
        else:
            logger.info("✓ No orphaned files found")
            
        return {"deleted_pdfs": deleted_pdfs, "deleted_covers": deleted_covers}
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return {"error": str(e)}

async def get_storage_stats():
    """Get detailed storage statistics"""
    try:
        # Book collection stats
        total_books = await book_collection.count_documents({})
        books_with_pdf = await book_collection.count_documents({"pdf_id": {"$exists": True}})
        books_with_cover = await book_collection.count_documents({"cover_id": {"$exists": True}})
        
        # GridFS stats
        pdf_files = await pdf_gridfs_bucket.find().to_list(length=None)
        cover_files = await cover_gridfs_bucket.find().to_list(length=None)
        
        # Calculate total sizes
        total_pdf_size = 0
        for pdf_file in pdf_files:
            total_pdf_size += pdf_file.length
            
        total_cover_size = 0
        for cover_file in cover_files:
            total_cover_size += cover_file.length
        
        return {
            "total_books": total_books,
            "books_with_pdf": books_with_pdf,
            "books_with_cover": books_with_cover,
            "total_pdf_files": len(pdf_files),
            "total_cover_files": len(cover_files),
            "total_pdf_size_mb": round(total_pdf_size / (1024 * 1024), 2),
            "total_cover_size_mb": round(total_cover_size / (1024 * 1024), 2),
            "total_storage_mb": round((total_pdf_size + total_cover_size) / (1024 * 1024), 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting storage stats: {e}")
        return None

async def close_connection():
    """ปิดการเชื่อมต่อ MongoDB"""
    try:
        client.close()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")

# Export GridFS buckets for use in other modules
__all__ = [
    'client', 'database', 'user_collection', 'book_collection',
    'pdf_gridfs_bucket', 'cover_gridfs_bucket',
    'test_connection', 'ensure_indexes', 'close_connection',
    'get_database_info', 'cleanup_orphaned_files', 'get_storage_stats'
]