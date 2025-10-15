from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import user_collection, book_collection
from app.auth.jwt_handler import get_current_user
from pydantic import BaseModel
from typing import List, Dict, Optional
from bson import ObjectId

router = APIRouter(prefix="/creator", tags=["Creator"])

class CreatorStats(BaseModel):
    total_followers: int
    total_readers: int
    total_likes: int
    total_sales: int
    total_books: int
    total_revenue: int

class SalesDataPoint(BaseModel):
    month: str
    value: int

class CreatorBook(BaseModel):
    id: str
    title: str
    price: int
    total_readers: int
    total_comments: int
    is_public: bool
    created_at: datetime

@router.get("/stats", response_model=CreatorStats)
async def get_creator_stats(current_user: dict = Depends(get_current_user)):
    """Get creator dashboard statistics"""
    try:
        username = current_user["username"]
        
        # Get all books by this creator
        creator_books = await book_collection.find(
            {"author": username}
        ).to_list(length=None)
        
        book_ids = [str(book["_id"]) for book in creator_books]
        
        # Count followers (users who have this creator in their following list)
        total_followers = await user_collection.count_documents(
            {"following": username}
        )
        
        # Count unique readers (users who own at least one book from this creator)
        readers_pipeline = [
            {"$match": {"library.book_id": {"$in": book_ids}}},
            {"$group": {"_id": "$username"}}
        ]
        readers_result = await user_collection.aggregate(readers_pipeline).to_list(length=None)
        total_readers = len(readers_result)
        
        # Count total likes across all creator's books
        total_likes = sum(book.get("likes", 0) for book in creator_books)
        
        # Count total sales (purchases of this creator's books)
        sales_pipeline = [
            {"$unwind": "$library"},
            {"$match": {"library.book_id": {"$in": book_ids}}},
            {"$group": {
                "_id": None,
                "total_sales": {"$sum": 1},
                "total_revenue": {"$sum": "$library.price_paid"}
            }}
        ]
        sales_result = await user_collection.aggregate(sales_pipeline).to_list(length=None)
        
        total_sales = 0
        total_revenue = 0
        if sales_result:
            total_sales = sales_result[0].get("total_sales", 0)
            total_revenue = sales_result[0].get("total_revenue", 0)
        
        return CreatorStats(
            total_followers=total_followers,
            total_readers=total_readers,
            total_likes=total_likes,
            total_sales=total_sales,
            total_books=len(creator_books),
            total_revenue=total_revenue
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get creator stats: {str(e)}")

@router.get("/sales/history", response_model=List[SalesDataPoint])
async def get_sales_history(
    current_user: dict = Depends(get_current_user),
    months: int = Query(6, ge=1, le=12, description="Number of months to retrieve")
):
    """Get sales history for the last N months"""
    try:
        username = current_user["username"]
        
        # Get all books by this creator
        creator_books = await book_collection.find(
            {"author": username}
        ).to_list(length=None)
        
        book_ids = [str(book["_id"]) for book in creator_books]
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30 * months)
        
        # Aggregate sales by month
        pipeline = [
            {"$unwind": "$library"},
            {"$match": {
                "library.book_id": {"$in": book_ids},
                "library.purchase_date": {"$gte": start_date, "$lte": end_date}
            }},
            {"$group": {
                "_id": {
                    "year": {"$year": "$library.purchase_date"},
                    "month": {"$month": "$library.purchase_date"}
                },
                "total_sales": {"$sum": 1}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        sales_result = await user_collection.aggregate(pipeline).to_list(length=None)
        
        # Format results
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        sales_data = []
        for item in sales_result:
            month_idx = item["_id"]["month"] - 1
            month_name = month_names[month_idx]
            sales_data.append(SalesDataPoint(
                month=month_name,
                value=item["total_sales"]
            ))
        
        # Fill in missing months with 0 sales
        if len(sales_data) < months:
            current = end_date
            for i in range(months):
                month_name = month_names[current.month - 1]
                if not any(d.month == month_name for d in sales_data):
                    sales_data.insert(0, SalesDataPoint(month=month_name, value=0))
                current = current - timedelta(days=30)
        
        return sales_data[-months:]  # Return last N months
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sales history: {str(e)}")

@router.get("/books", response_model=List[CreatorBook])
async def get_creator_books(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get all books created by the current user"""
    try:
        username = current_user["username"]
        
        # Get creator's books
        books = await book_collection.find(
            {"author": username}
        ).skip(skip).limit(limit).sort("created_at", -1).to_list(length=limit)
        
        result = []
        for book in books:
            book_id = str(book["_id"])
            
            # Count unique readers for this book
            readers_count = await user_collection.count_documents(
                {"library.book_id": book_id}
            )
            
            # Count comments (you'll need to implement comments system)
            comments_count = book.get("comments_count", 0)
            
            result.append(CreatorBook(
                id=book_id,
                title=book["title"],
                price=book.get("price", 0),
                total_readers=readers_count,
                total_comments=comments_count,
                is_public=book.get("is_public", True),
                created_at=book.get("created_at", datetime.utcnow())
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get creator books: {str(e)}")

@router.post("/follow/{creator_username}")
async def follow_creator(
    creator_username: str,
    current_user: dict = Depends(get_current_user)
):
    """Follow a creator"""
    try:
        if current_user["username"] == creator_username:
            raise HTTPException(status_code=400, detail="Cannot follow yourself")
        
        # Check if creator exists
        creator = await user_collection.find_one({"username": creator_username})
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        # Add to following list
        result = await user_collection.update_one(
            {"username": current_user["username"]},
            {"$addToSet": {"following": creator_username}}
        )
        
        if result.modified_count == 0:
            return {"message": "Already following this creator"}
        
        return {"message": f"Successfully followed {creator_username}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to follow creator: {str(e)}")

@router.delete("/unfollow/{creator_username}")
async def unfollow_creator(
    creator_username: str,
    current_user: dict = Depends(get_current_user)
):
    """Unfollow a creator"""
    try:
        result = await user_collection.update_one(
            {"username": current_user["username"]},
            {"$pull": {"following": creator_username}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Not following this creator")
        
        return {"message": f"Successfully unfollowed {creator_username}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unfollow creator: {str(e)}")
    
@router.get("/profile/{username}")
async def get_user_profile(
    username: str,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Get public profile information by username (creator or normal user)"""
    
    user = await user_collection.find_one({"username": username})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # --- สรุปข้อมูลพื้นฐาน ---
    followers_count = await user_collection.count_documents({"following": username})
    following_count = len(user.get("following", []))

    # --- นับจำนวนหนังสือถ้ามี ---
    books = await book_collection.find({"author": username}).to_list(None)
    total_books = len(books)
    
    # --- นับยอดขายถ้ามี (ถ้าเป็น creator เท่านั้น) ---
    total_sales = 0
    if books:
        pipeline = [
            {"$unwind": "$library"},
            {"$match": {"library.book_id": {"$in": [str(book["_id"]) for book in books]}}},
            {"$group": {"_id": None, "total_revenue": {"$sum": "$library.price_paid"}}}
        ]
        result = await user_collection.aggregate(pipeline).to_list(length=None)
        if result:
            total_sales = int(result[0].get("total_revenue", 0))
    
    # --- ตรวจสอบว่า current user follow อยู่มั้ย ---
    is_following = False
    if current_user:
        me = await user_collection.find_one({"username": current_user["username"]})
        if me:
            is_following = username in me.get("following", [])

    return {
        "username": user["username"],
        "profile_picture": user.get("profile_picture"),
        "bio": user.get("bio", ""),
        "followers_count": followers_count,
        "following_count": following_count,
        "total_books": total_books,
        "total_sales": total_sales,
        "joined_date": user.get("created_at"),
        "role": user.get("role", "user"),
        "is_following": is_following
    }