import httpx
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from app.database import book_collection
from app.auth.jwt_handler import get_current_user
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from bson import ObjectId
import os
import uuid

router = APIRouter(prefix="/books", tags=["Books"])

# Define available categories
AVAILABLE_CATEGORIES = [
    "ความรู้",      # Knowledge
    "นิยาย",        # Fiction
    "มังงะ",        # Manga
    "ศิลปะ",        # Art
    "วิทยาศาสตร์",   # Science
    "ประวัติศาสตร์", # History
    "ธุรกิจ",       # Business
    "การศึกษา",     # Education
    "เทคโนโลยี",    # Technology
    "สุขภาพ",       # Health
    "การเงิน",      # Finance
    "จิตวิทยา",     # Psychology
    "อื่นๆ"         # Others
]

class BookCreate(BaseModel):
    title: str
    author: str
    rating: float
    description: str
    category: str = "อื่นๆ"
    price: int = 0

class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    cover: Optional[str] = None
    rating: float
    description: str
    category: str
    price: int = 0
    created_at: datetime

class CategoryResponse(BaseModel):
    categories: List[str]

# Helper function to check if user is admin
async def is_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role", "reader") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/categories", response_model=CategoryResponse)
async def get_categories(current_user: dict = Depends(get_current_user)):
    """Get all available book categories."""
    return CategoryResponse(categories=AVAILABLE_CATEGORIES)

@router.post("/", response_model=BookResponse)
async def upload_book(
    title: str = Form(...),
    rating: float = Form(...),
    description: str = Form(...),
    category: str = Form("อื่นๆ"),
    price: int = Form(0),  # เพิ่มฟิลด์ price
    cover_file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(is_admin)
):
    """Upload/create a new book. Admin only. Supports optional cover image upload."""
    
    # Validate category
    if category not in AVAILABLE_CATEGORIES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid category. Available categories: {', '.join(AVAILABLE_CATEGORIES)}"
        )
    
    # Create book dict from Form data
    book_dict = {
        "title": title,
        "author": current_user["username"],  # ใช้ชื่อผู้ใช้จาก JWT token
        "rating": rating,
        "description": description,
        "category": category,
        "price": price,
        "created_at": datetime.utcnow(),
        "uploader": current_user["username"]  # เก็บไว้สำหรับอ้างอิง
    }
    
    # Handle cover upload if provided
    cover_url = None
    if cover_file and cover_file.filename:
        # Validate file type
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
        file_extension = cover_file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join("static/covers", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            with open(file_path, "wb") as f:
                content = await cover_file.read()
                f.write(content)
            
            cover_url = f"/static/covers/{filename}"
            book_dict["cover"] = cover_url
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save cover image: {str(e)}")

    # Insert into MongoDB
    try:
        result = await book_collection.insert_one(book_dict)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create book")

        created_book = await book_collection.find_one({"_id": result.inserted_id})
        
        return BookResponse(
            id=str(created_book["_id"]),
            title=created_book["title"],
            author=created_book["author"],
            cover=created_book.get("cover"),
            rating=created_book["rating"],
            description=created_book["description"],
            category=created_book.get("category", "อื่นๆ"),
            price=created_book.get("price", 0),
            created_at=created_book["created_at"]
        )
        
    except Exception as e:
        # Delete uploaded file if DB insert failed
        if cover_url and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{book_id}", response_model=BookResponse)
async def get_book_detail(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get details of a specific book by ID."""
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid book ID format")
            
        book = await book_collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        return BookResponse(
            id=str(book["_id"]),
            title=book["title"],
            author=book["author"],
            cover=book.get("cover"),
            rating=book["rating"],
            description=book["description"],
            category=book.get("category", "อื่นๆ"),
            price=book.get("price", 0),
            created_at=book.get("created_at", datetime.utcnow())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/", response_model=list[BookResponse])
async def get_all_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title or author"),
    sort_by: str = Query("created_at", description="Sort by: created_at, rating, title"),
    sort_order: int = Query(-1, description="Sort order: 1 (asc) or -1 (desc)"),
    current_user: dict = Depends(get_current_user)
):
    """Get all books with pagination, filtering, and search."""
    try:
        # Build query filter
        query_filter = {}
        
        # Category filter
        if category and category != "ทั้งหมด":
            if category not in AVAILABLE_CATEGORIES:
                raise HTTPException(status_code=400, detail="Invalid category")
            query_filter["category"] = category
        
        # Search filter
        if search:
            query_filter["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"author": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        # Validate sort parameters
        valid_sort_fields = ["created_at", "rating", "title", "author"]
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"
        
        if sort_order not in [1, -1]:
            sort_order = -1
        
        # Execute query
        cursor = book_collection.find(query_filter).skip(skip).limit(limit).sort(sort_by, sort_order)
        books = await cursor.to_list(length=limit)
        
        return [
            BookResponse(
                id=str(book["_id"]),
                title=book["title"],
                author=book["author"],
                cover=book.get("cover"),
                rating=book["rating"],
                description=book["description"],
                category=book.get("category", "อื่นๆ"),
                price=book.get("price", 0),
                created_at=book.get("created_at", datetime.utcnow())
            )
            for book in books
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/category/{category}", response_model=list[BookResponse])
async def get_books_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get books by specific category."""
    try:
        if category not in AVAILABLE_CATEGORIES:
            raise HTTPException(status_code=400, detail="Invalid category")
        
        cursor = book_collection.find({"category": category}).skip(skip).limit(limit).sort("created_at", -1)
        books = await cursor.to_list(length=limit)
        
        return [
            BookResponse(
                id=str(book["_id"]),
                title=book["title"],
                author=book["author"],
                cover=book.get("cover"),
                rating=book["rating"],
                description=book["description"],
                category=book.get("category", "อื่นๆ"),
                price=book.get("price", 0),
                created_at=book.get("created_at", datetime.utcnow())
            )
            for book in books
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/stats/categories", response_model=Dict[str, int])
async def get_category_stats(current_user: dict = Depends(get_current_user)):
    """Get book count for each category."""
    try:
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        result = await book_collection.aggregate(pipeline).to_list(length=None)
        
        # Convert to dict and ensure all categories are included
        stats = {item["_id"] or "อื่นๆ": item["count"] for item in result}
        
        # Add missing categories with 0 count
        for category in AVAILABLE_CATEGORIES:
            if category not in stats:
                stats[category] = 0
                
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")