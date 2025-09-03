from fastapi import FastAPI
from app.routers import auth
# from app.routers import users  # comment ไว้ก่อน

app = FastAPI(title="FastAPI JWT MongoDB Auth")

app.include_router(auth.router)
# app.include_router(users.router)  # comment ไว้ก่อน

@app.get("/")
def root():
    return {"message": "JWT Auth with MongoDB"}