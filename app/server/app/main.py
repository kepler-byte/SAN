from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users
from .database.connection import connect_to_db, close_db_connection

app = FastAPI(title="LibroBook API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ปรับตาม frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# เชื่อมต่อ database
@app.on_event("startup")
async def startup_db_client():
    await connect_to_db()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_db_connection()

# ลงทะเบียน routers
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to LibroBook API!"}