# server/main.py
from fastapi import FastAPI
from .routers import users

app = FastAPI(title="My API")

app.include_router(users.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}