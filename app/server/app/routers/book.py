import io
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple

import gridfs
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from pydantic import BaseModel

from app.auth.jwt_handler import get_current_user
from app.database import database, book_collection, user_collection

# ============ INITIALIZATION ============

router = APIRouter(prefix="/books", tags=["Books"])

# Initialize GridFS buckets
pdf_bucket = AsyncIOMotorGridFSBucket(database, bucket_name="pdfs")
cover_bucket = AsyncIOMotorGridFSBucket(database, bucket_name="covers")

# Available book categories
AVAILABLE_CATEGORIES = [
    "ความรู้", "นิยาย", "มังงะ", "ศิลปะ", "วิทยาศาสตร์", 
    "ประวัติศาสตร์", "ธุรกิจ", "การศึกษา", "เทคโนโลยี", 
    "สุขภาพ", "การเงิน", "จิตวิทยา", "อื่นๆ"
]

# ============ MODELS ============

class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    cover_id: Optional[str] = None
    pdf_id: Optional[str] = None
    rating: float
    description: str
    category: str
    price: int = 0
    created_at: datetime
    file_size: Optional[int] = None
    has_pdf: bool = False
    has_cover: bool = False

class CategoryResponse(BaseModel):
    categories: List[str]

class ReadingProgressUpdate(BaseModel):
    book_id: str
    page: Optional[int] = None
    progress_percentage: Optional[float] = None
    status: Optional[str] = None  # "reading", "completed", "paused"

class ReadingSessionResponse(BaseModel):
    book_id: str
    book_title: str
    current_page: int
    total_pages: int
    progress_percentage: float
    status: str
    last_read: datetime
    started_at: datetime

# ============ HELPER FUNCTIONS ============

async def upload_file_to_gridfs(file: UploadFile, bucket: AsyncIOMotorGridFSBucket, file_type: str) -> Tuple[ObjectId, int]:
    """Upload file to GridFS and return file ID and size"""
    try:
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        max_size = 100 * 1024 * 1024 if file_type == "pdf" else 5 * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size for {file_type}: {max_size // (1024*1024)}MB"
            )
        
        # Create metadata
        metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "upload_date": datetime.utcnow(),
            "file_type": file_type,
            "original_size": file_size
        }
        
        # Upload to GridFS
        file_id = await bucket.upload_from_stream(
            filename=f"{file_type}_{uuid.uuid4()}_{file.filename}",
            source=io.BytesIO(content),
            metadata=metadata
        )
        
        return file_id, file_size
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload {file_type}: {str(e)}")

async def download_file_from_gridfs(file_id: ObjectId, bucket: AsyncIOMotorGridFSBucket) -> Tuple[bytes, str, str]:
    """Download file from GridFS"""
    try:
        # Check if file exists
        if not await bucket.find({"_id": file_id}).to_list(length=1):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get file info
        grid_out = await bucket.open_download_stream(file_id)
        
        # Read file content
        content = await grid_out.read()
        
        # Get metadata
        metadata = grid_out.metadata or {}
        content_type = metadata.get("content_type", "application/octet-stream")
        filename = metadata.get("filename", f"file_{file_id}")
        
        return content, content_type, filename
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

async def is_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Check if current user is an admin"""
    if current_user.get("role", "reader") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def get_reading_collection():
    """Get or create reading tracking collection"""
    return database.reading_sessions

async def get_recommendations_collection():
    """Get recommendations collection"""
    return database.recommendations

async def validate_book_id(book_id: str) -> ObjectId:
    """Validate and convert book_id to ObjectId"""
    if not ObjectId.is_valid(book_id):
        raise HTTPException(status_code=400, detail="Invalid book ID format")
    return ObjectId(book_id)

async def get_book_by_id(book_id: str) -> dict:
    """Get book by ID or raise 404 if not found"""
    book = await book_collection.find_one({"_id": await validate_book_id(book_id)})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# ============ CATEGORY ENDPOINTS ============

@router.get("/categories", response_model=CategoryResponse)
async def get_categories(current_user: dict = Depends(get_current_user)):
    """Get all available book categories."""
    return CategoryResponse(categories=AVAILABLE_CATEGORIES)

# ============ BOOK CRUD ENDPOINTS ============

@router.post("/", response_model=BookResponse)
async def upload_book(
    title: str = Form(...),
    rating: float = Form(...),
    description: str = Form(...),
    category: str = Form("อื่นๆ"),
    price: int = Form(0),
    cover_file: Optional[UploadFile] = File(None),
    pdf_file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(is_admin)
):
    """Upload/create a new book with cover and PDF support using GridFS."""
    
    # Validate category
    if category not in AVAILABLE_CATEGORIES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid category. Available categories: {', '.join(AVAILABLE_CATEGORIES)}"
        )
    
    # Create book metadata
    book_dict = {
        "title": title,
        "author": current_user["username"],
        "rating": rating,
        "description": description,
        "category": category,
        "price": price,
        "created_at": datetime.utcnow(),
        "uploader": current_user["username"]
    }
    
    # Handle cover upload
    if cover_file and cover_file.filename:
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
        file_extension = cover_file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid cover file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        try:
            cover_id, _ = await upload_file_to_gridfs(cover_file, cover_bucket, "cover")
            book_dict["cover_id"] = cover_id
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload cover: {str(e)}")
    
    # Handle PDF upload
    if pdf_file and pdf_file.filename:
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        try:
            pdf_id, file_size = await upload_file_to_gridfs(pdf_file, pdf_bucket, "pdf")
            book_dict["pdf_id"] = pdf_id
            book_dict["file_size"] = file_size
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload PDF: {str(e)}")
    
    # Insert book metadata into MongoDB
    try:
        result = await book_collection.insert_one(book_dict)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create book")

        created_book = await book_collection.find_one({"_id": result.inserted_id})
        if not created_book:
            raise HTTPException(status_code=500, detail="Failed to retrieve created book from database")
        
        return BookResponse(
            id=str(created_book["_id"]),
            title=created_book["title"],
            author=created_book["author"],
            cover_id=str(created_book["cover_id"]) if created_book.get("cover_id") else None,
            pdf_id=str(created_book["pdf_id"]) if created_book.get("pdf_id") else None,
            rating=created_book["rating"],
            description=created_book["description"],
            category=created_book.get("category", "อื่นๆ"),
            price=created_book.get("price", 0),
            created_at=created_book["created_at"],
            file_size=created_book.get("file_size"),
            has_pdf=bool(created_book.get("pdf_id")),
            has_cover=bool(created_book.get("cover_id"))
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{book_id}", response_model=BookResponse)
async def get_book_detail(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get details of a specific book by ID."""
    try:
        book = await get_book_by_id(book_id)
        
        return BookResponse(
            id=str(book["_id"]),
            title=book["title"],
            author=book["author"],
            cover_id=str(book["cover_id"]) if book.get("cover_id") else None,
            pdf_id=str(book["pdf_id"]) if book.get("pdf_id") else None,
            rating=book["rating"],
            description=book["description"],
            category=book.get("category", "อื่นๆ"),
            price=book.get("price", 0),
            created_at=book.get("created_at", datetime.utcnow()),
            file_size=book.get("file_size"),
            has_pdf=bool(book.get("pdf_id")),
            has_cover=bool(book.get("cover_id"))
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
        
        if category and category != "ทั้งหมด":
            if category not in AVAILABLE_CATEGORIES:
                raise HTTPException(status_code=400, detail="Invalid category")
            query_filter["category"] = category
        
        if search:
            query_filter["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"author": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        valid_sort_fields = ["created_at", "rating", "title", "author"]
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"
        
        if sort_order not in [1, -1]:
            sort_order = -1
        
        cursor = book_collection.find(query_filter).skip(skip).limit(limit).sort(sort_by, sort_order)
        books = await cursor.to_list(length=limit)
        
        return [
            BookResponse(
                id=str(book["_id"]),
                title=book["title"],
                author=book["author"],
                cover_id=str(book["cover_id"]) if book.get("cover_id") else None,
                pdf_id=str(book["pdf_id"]) if book.get("pdf_id") else None,
                rating=book["rating"],
                description=book["description"],
                category=book.get("category", "อื่นๆ"),
                price=book.get("price", 0),
                created_at=book.get("created_at", datetime.utcnow()),
                file_size=book.get("file_size"),
                has_pdf=bool(book.get("pdf_id")),
                has_cover=bool(book.get("cover_id"))
            )
            for book in books
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.delete("/{book_id}")
async def delete_book(
    book_id: str,
    current_user: dict = Depends(is_admin)
):
    """Delete a book and its associated files from GridFS."""
    try:
        book = await get_book_by_id(book_id)
        
        # Delete associated files from GridFS
        if book.get("cover_id"):
            await cover_bucket.delete(ObjectId(book["cover_id"]))
        
        if book.get("pdf_id"):
            await pdf_bucket.delete(ObjectId(book["pdf_id"]))
        
        # Delete book metadata
        result = await book_collection.delete_one({"_id": ObjectId(book_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Book not found")
        
        return {"message": "Book and associated files deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# ============ FILE ACCESS ENDPOINTS ============

@router.get("/{book_id}/cover")
async def get_book_cover(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get book cover image from GridFS."""
    try:
        book = await get_book_by_id(book_id)
        
        cover_id = book.get("cover_id")
        if not cover_id:
            raise HTTPException(status_code=404, detail="Cover not available for this book")
        
        # Download cover from GridFS
        content, content_type, filename = await download_file_from_gridfs(ObjectId(cover_id), cover_bucket)
        
        return StreamingResponse(
            io.BytesIO(content),
            media_type=content_type,
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/{book_id}/read")
async def read_book(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Stream PDF for reading from GridFS."""
    try:
        book = await get_book_by_id(book_id)
        
        pdf_id = book.get("pdf_id")
        if not pdf_id:
            raise HTTPException(status_code=404, detail="PDF not available for this book")
        
        # Add your business logic here:
        # - Check if user has purchased the book
        # - Check subscription status
        # - Implement reading limits, etc.
        
        # Download PDF from GridFS
        content, content_type, filename = await download_file_from_gridfs(ObjectId(pdf_id), pdf_bucket)
        
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Content-Type": "application/pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/{book_id}/download")
async def download_book(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Download PDF file from GridFS."""
    try:
        book = await get_book_by_id(book_id)
        
        pdf_id = book.get("pdf_id")
        if not pdf_id:
            raise HTTPException(status_code=404, detail="PDF not available for this book")
        
        # Add download permission checks here
        
        # Download PDF from GridFS
        content, content_type, filename = await download_file_from_gridfs(ObjectId(pdf_id), pdf_bucket)
        
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# ============ READING TRACKING ENDPOINTS ============

@router.patch("/reading/progress")
async def update_reading_progress(
    progress_data: ReadingProgressUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update reading progress for a book"""
    try:
        book_id = await validate_book_id(progress_data.book_id)
        reading_collection = await get_reading_collection()
        user_id = ObjectId(current_user["user_id"])
        
        # Build update data
        update_dict = {
            "last_read": datetime.utcnow(),
            "status": progress_data.status or "reading"
        }
        
        if progress_data.page is not None:
            update_dict["current_page"] = progress_data.page
        
        if progress_data.progress_percentage is not None:
            update_dict["progress_percentage"] = progress_data.progress_percentage
        
        result = await reading_collection.update_one(
            {
                "user_id": user_id,
                "book_id": book_id
            },
            {
                "$set": update_dict,
                "$setOnInsert": {
                    "started_at": datetime.utcnow(),
                    "user_id": user_id,
                    "book_id": book_id
                }
            },
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Progress updated",
            "book_id": progress_data.book_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reading/in-progress", response_model=list[ReadingSessionResponse])
async def get_reading_in_progress(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get books currently being read"""
    try:
        reading_collection = await get_reading_collection()
        user_id = ObjectId(current_user["user_id"])
        
        cursor = reading_collection.find({
            "user_id": user_id,
            "status": {"$in": ["reading", "paused"]}
        }).skip(skip).limit(limit).sort("last_read", -1)
        
        sessions = await cursor.to_list(length=limit)
        
        # Fetch book titles
        result = []
        for session in sessions:
            book = await book_collection.find_one({"_id": session["book_id"]})
            if book:
                result.append(ReadingSessionResponse(
                    book_id=str(session["book_id"]),
                    book_title=book["title"],
                    current_page=session.get("current_page", 0),
                    total_pages=session.get("total_pages", 0),
                    progress_percentage=session.get("progress_percentage", 0),
                    status=session.get("status", "reading"),
                    last_read=session.get("last_read", datetime.utcnow()),
                    started_at=session.get("started_at", datetime.utcnow())
                ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reading/completed", response_model=list[ReadingSessionResponse])
async def get_completed_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get completed books"""
    try:
        reading_collection = await get_reading_collection()
        user_id = ObjectId(current_user["user_id"])
        
        cursor = reading_collection.find({
            "user_id": user_id,
            "status": "completed"
        }).skip(skip).limit(limit).sort("last_read", -1)
        
        sessions = await cursor.to_list(length=limit)
        
        result = []
        for session in sessions:
            book = await book_collection.find_one({"_id": session["book_id"]})
            if book:
                result.append(ReadingSessionResponse(
                    book_id=str(session["book_id"]),
                    book_title=book["title"],
                    current_page=session.get("current_page", 0),
                    total_pages=session.get("total_pages", 0),
                    progress_percentage=session.get("progress_percentage", 100),
                    status="completed",
                    last_read=session.get("last_read", datetime.utcnow()),
                    started_at=session.get("started_at", datetime.utcnow())
                ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reading/completed")
async def mark_book_completed(
    book_id: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Mark a book as completed"""
    try:
        book_id_obj = await validate_book_id(book_id)
        reading_collection = await get_reading_collection()
        user_id = ObjectId(current_user["user_id"])
        
        await reading_collection.update_one(
            {
                "user_id": user_id,
                "book_id": book_id_obj
            },
            {
                "$set": {
                    "status": "completed",
                    "progress_percentage": 100,
                    "completed_at": datetime.utcnow(),
                    "last_read": datetime.utcnow()
                }
            }
        )
        
        return {"success": True, "message": "Book marked as completed"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ RECOMMENDATION ENDPOINTS ============

@router.get("/recommend/personalized")
async def get_personalized_recommendations(
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """Get personalized book recommendations based on reading history"""
    try:
        reading_collection = await get_reading_collection()
        user_id = ObjectId(current_user["user_id"])
        
        # Get user's reading history
        user_readings = await reading_collection.find({
            "user_id": user_id
        }).to_list(length=None)
        
        if not user_readings:
            # No history: return random popular books
            books = await book_collection.find({}).sort("rating", -1).limit(limit).to_list(length=limit)
        else:
            # Get categories from read books
            read_book_ids = [r["book_id"] for r in user_readings]
            read_books = await book_collection.find(
                {"_id": {"$in": read_book_ids}}
            ).to_list(length=None)
            
            # Extract categories
            categories = list(set([b.get("category", "อื่นๆ") for b in read_books]))
            
            # Find similar books not yet read
            books = await book_collection.find({
                "_id": {"$nin": read_book_ids},
                "category": {"$in": categories}
            }).sort("rating", -1).limit(limit).to_list(length=limit)
            
            # If not enough, fill with popular books
            if len(books) < limit:
                remaining = limit - len(books)
                additional = await book_collection.find({
                    "_id": {"$nin": read_book_ids}
                }).sort("rating", -1).limit(remaining).to_list(length=remaining)
                books.extend(additional)
        
        return [
            {
                "id": str(b["_id"]),
                "title": b["title"],
                "author": b["author"],
                "rating": b.get("rating", 0),
                "category": b.get("category", "อื่นๆ"),
                "price": b.get("price", 0),
                "description": b.get("description", ""),
                "created_at": b.get("created_at", datetime.utcnow()),
                "has_cover": "cover_id" in b,
                "has_pdf": "pdf_id" in b
            }
            for b in books[:limit]
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend/category/{category}")
async def get_category_recommendations(
    category: str,
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """Get book recommendations for a specific category"""
    try:
        if category not in AVAILABLE_CATEGORIES:
            raise HTTPException(status_code=400, detail="Invalid category")
        
        books = await book_collection.find(
            {"category": category}
        ).sort("rating", -1).limit(limit).to_list(length=limit)
        
        return [
            {
                "id": str(b["_id"]),
                "title": b["title"],
                "author": b["author"],
                "rating": b.get("rating", 0),
                "category": b.get("category", "อื่นๆ"),
                "price": b.get("price", 0)
            }
            for b in books
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ STATISTICS ENDPOINTS ============

@router.get("/stats/storage")
async def get_storage_stats(current_user: dict = Depends(is_admin)):
    """Get storage statistics for GridFS."""
    try:
        # Get book count and total file sizes
        pipeline = [
            {"$match": {"file_size": {"$exists": True}}},
            {"$group": {
                "_id": None,
                "total_books": {"$sum": 1},
                "total_pdf_size": {"$sum": "$file_size"},
                "avg_pdf_size": {"$avg": "$file_size"}
            }}
        ]
        
        result = await book_collection.aggregate(pipeline).to_list(length=None)
        
        # Get GridFS bucket stats
        pdf_files_count = await pdf_bucket.find().to_list(length=None)
        cover_files_count = await cover_bucket.find().to_list(length=None)
        
        if result:
            stats = result[0]
            return {
                "total_books": stats["total_books"],
                "total_pdf_size_mb": round(stats["total_pdf_size"] / (1024*1024), 2),
                "average_pdf_size_mb": round(stats["avg_pdf_size"] / (1024*1024), 2),
                "pdf_files_in_gridfs": len(pdf_files_count),
                "cover_files_in_gridfs": len(cover_files_count)
            }
        else:
            return {
                "total_books": 0,
                "total_pdf_size_mb": 0,
                "average_pdf_size_mb": 0,
                "pdf_files_in_gridfs": len(pdf_files_count),
                "cover_files_in_gridfs": len(cover_files_count)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/stats/reading")
async def get_reading_stats(current_user: dict = Depends(get_current_user)):
    """Get reading statistics for current user"""
    try:
        reading_collection = await get_reading_collection()
        user_id = ObjectId(current_user["user_id"])
        
        total_read = await reading_collection.count_documents({
            "user_id": user_id,
            "status": "completed"
        })
        
        in_progress = await reading_collection.count_documents({
            "user_id": user_id,
            "status": "reading"
        })
        
        # Calculate reading streak (consecutive days)
        last_30_days = datetime.utcnow() - timedelta(days=30)
        recent_reads = await reading_collection.find({
            "user_id": user_id,
            "last_read": {"$gte": last_30_days}
        }).to_list(length=None)
        
        return {
            "total_completed": total_read,
            "currently_reading": in_progress,
            "recent_activity_30_days": len(recent_reads),
            "user_id": str(user_id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
