from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging

# Import your routers
from app.routers import auth
from app.routers import users
from app.routers import book
from app.database import test_connection

# กำหนด logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FastAPI JWT Auth", version="1.0.0")

# CORS middleware - แก้ไขให้ครอบคลุมมากขึ้น
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

# Error handler สำหรับ 500 errors
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

# สร้าง folder static/covers ถ้ายังไม่มี
os.makedirs("static/covers", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(users.router) 
app.include_router(book.router) 

@app.get("/")
async def root():
    return {"message": "FastAPI JWT Auth with Books API"}

@app.get("/health")
async def health_check():
    # ตรวจสอบการเชื่อมต่อ MongoDB
    db_status = await test_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected"
    }

# Import database functions
from app.database import test_connection, ensure_indexes, close_connection

# Startup event เพื่อทดสอบการเชื่อมต่อ
@app.on_event("startup")
async def startup_event():
    logger.info("Starting FastAPI application...")
    db_connected = await test_connection()
    if not db_connected:
        logger.warning("Warning: MongoDB connection failed during startup")
    else:
        # สร้าง indexes ที่จำเป็น
        await ensure_indexes()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down FastAPI application...")
    await close_connection()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)