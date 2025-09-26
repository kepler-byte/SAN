from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

# Import your routers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
from app.routers import users
from app.routers import book

app = FastAPI(title="FastAPI JWT Auth", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ปรับให้เหมาะสมกับ production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)