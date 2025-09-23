from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
# from app.routers import users  # comment ไว้ก่อน

app = FastAPI(title="FastAPI JWT MongoDB Auth")

app.include_router(auth.router)
# app.include_router(users.router)  # comment ไว้ก่อน

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # origin ของ frontend
    allow_credentials=True,
    allow_methods=["*"],  # หรือจะเจาะจง ["POST", "GET"]
    allow_headers=["*"],  # เช่น Content-Type, Authorization
)

@app.get("/")
def root():
    return {"message": "JWT Auth with MongoDB"}