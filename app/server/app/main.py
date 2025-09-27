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
    return {"status": "healthy"}

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