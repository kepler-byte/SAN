from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
from app.routers import users  

app = FastAPI(title="FastAPI JWT MongoDB Auth")

app.include_router(auth.router)
app.include_router(users.router)  

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/")
def root():
    return {"message": "JWT Auth with MongoDB"}