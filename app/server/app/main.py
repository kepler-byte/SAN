from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging

# Import your routers
from app.routers import auth
from app.routers import users
from app.routers import book  # This will now use GridFS
from app.database import test_connection, get_database_info, get_storage_stats

# กำหนด logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Welcome to SAN Endpoint APi!", 
    version="1.0.0",
    description="Book management API with MongoDB GridFS for PDF and image storage"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "*"  # ใน production ควรระบุ domain เฉพาะ
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Error handlers
@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.exception_handler(413)
async def file_too_large_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=413,
        content={"detail": "File too large. Please upload a smaller file."},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Include routers
app.include_router(auth.router)
app.include_router(users.router) 
app.include_router(book.router)  # Now uses GridFS

@app.get("/")
async def root():
    return {
        "message": "FastAPI JWT Auth with GridFS Book Storage",
        "version": "1.0.0",
        "features": [
            "JWT Authentication",
            "Book Management",
            "PDF Upload/Storage via GridFS",
            "Cover Image Support",
            "Category Management",
            "Search & Filtering"
        ]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check including GridFS"""
    db_status = await test_connection()
    db_info = await get_database_info() if db_status else None
    storage_stats = await get_storage_stats() if db_status else None
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "mongodb_info": db_info,
        "storage_stats": storage_stats,
        "gridfs_enabled": True
    }

@app.get("/debug")
async def debug_endpoint():
    """Debug endpoint with detailed GridFS information"""
    try:
        db_connected = await test_connection()
        db_info = await get_database_info()
        storage_stats = await get_storage_stats()
        
        return {
            "mongodb_connection": "success" if db_connected else "failed",
            "database_info": db_info,
            "storage_stats": storage_stats,
            "gridfs_status": "enabled",
            "message": "Check logs for detailed information"
        }
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        return {
            "mongodb_connection": "failed",
            "error": str(e),
            "message": "Check logs for detailed error information"
        }

@app.get("/admin/storage")
async def admin_storage_info():
    """Admin endpoint for storage management"""
    try:
        from app.auth.jwt_handler import get_current_user
        from fastapi import Depends
        
        # This would normally have authentication, but for testing:
        storage_stats = await get_storage_stats()
        db_info = await get_database_info()
        
        return {
            "storage_statistics": storage_stats,
            "database_info": db_info,
            "recommendations": [
                "Regularly clean up orphaned files",
                "Monitor total storage usage",
                "Consider file size limits for uploads"
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/admin/cleanup")
async def admin_cleanup():
    """Admin endpoint to clean up orphaned GridFS files"""
    try:
        from app.database import cleanup_orphaned_files
        result = await cleanup_orphaned_files()
        return {
            "cleanup_result": result,
            "message": "Cleanup completed successfully"
        }
    except Exception as e:
        return {"error": str(e)}

# Import database functions
from app.database import ensure_indexes, close_connection

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting FastAPI application with GridFS support...")
    
    # Test database connection
    db_connected = await test_connection()
    
    if not db_connected:
        logger.warning("⚠️  WARNING: MongoDB connection failed during startup")
        logger.warning("⚠️  Application will continue but database operations will fail")
        logger.warning("⚠️  Check your MongoDB URI and network connectivity")
    else:
        logger.info("✅ MongoDB connected successfully")
        
        # Create necessary indexes
        try:
            await ensure_indexes()
            logger.info("✅ Database indexes created")
        except Exception as e:
            logger.warning(f"⚠️  Index creation failed: {e}")
        
        # Log database info
        try:
            db_info = await get_database_info()
            if db_info:
                logger.info(f"📊 Database: {db_info['database_name']}")
                logger.info(f"📊 Collections: {len(db_info['collections'])}")
                logger.info(f"📊 GridFS collections: {len(db_info['gridfs_collections'])}")
                
            storage_stats = await get_storage_stats()
            if storage_stats:
                logger.info(f"💾 Total books: {storage_stats['total_books']}")
                logger.info(f"💾 Total storage: {storage_stats['total_storage_mb']} MB")
                
        except Exception as e:
            logger.warning(f"⚠️  Could not retrieve database info: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down FastAPI application...")
    await close_connection()

# Additional middleware for file uploads
@app.middleware("http")
async def add_file_upload_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Add headers for file upload support
    if request.url.path.startswith("/books") and request.method == "POST":
        response.headers["Accept-Ranges"] = "bytes"
        response.headers["Access-Control-Expose-Headers"] = "Content-Range, Content-Length"
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        # Increase timeout for large file uploads
        timeout_keep_alive=300,
        # Allow larger request bodies for PDF uploads
        limit_max_requests=1000
    )
