from fastapi import APIRouter, Depends, HTTPException
from ..schemas.user import UserCreate, UserResponse
from ..database.connection import database
from bson import ObjectId

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    user_dict = user.dict()
    result = await database.users.insert_one(user_dict)
    new_user = await database.users.find_one({"_id": result.inserted_id})
    return {
        "id": str(new_user["_id"]),
        "name": new_user["name"],
        "email": new_user["email"]
    }

@router.get("/", response_model=list[UserResponse])
async def get_users():
    users_cursor = database.users.find()
    users = []
    async for user in users_cursor:
        users.append({
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"]
        })
    return users