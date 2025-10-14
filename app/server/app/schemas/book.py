import gridfs
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from datetime import datetime #สำหรับจัดการวันที่และเวลา
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query #สำหรับสร้าง API routes และจัดการการอัปโหลดไฟล์
from fastapi.responses import StreamingResponse #สำหรับส่งไฟล์เป็นสตรีมไปยังลูกค้า
from app.database import database 
from app.auth.jwt_handler import get_current_user
from pydantic import BaseModel #สำหรับการสร้างโมเดลข้อมูลที่ใช้ในการตรวจสอบและจัดการข้อมูล
from typing import Optional, Dict, Any, List #สำหรับการระบุชนิดข้อมูล
from bson import ObjectId #สำหรับจัดการกับ ObjectId ของ MongoDB ซึ่ง ObjectId เป็นชนิดข้อมูลเฉพาะที่ใช้เป็นตัวระบุเอกลักษณ์ของเอกสารใน MongoDB
import io #สำหรับการจัดการกับ I/O operations เช่น การอ่านและเขียนไฟล์ในหน่วยความจำ
import uuid #uuid คือโมดูลใน Python ที่ใช้สำหรับสร้างตัวระบุเอกลักษณ์แบบสุ่ม (UUID - Universally Unique Identifier) ซึ่งมีประโยชน์ในการสร้าง ID ที่ไม่ซ้ำกันสำหรับวัตถุต่าง ๆ เช่น ไฟล์หรือรายการในฐานข้อมูล

router = APIRouter(prefix="/books", tags=["Books"]) #สร้าง router สำหรับจัดการเส้นทางที่เกี่ยวข้องกับหนังสือ โดยมี prefix เป็น /books และแท็กเป็น "Books"

# Initialize GridFS buckets เพื่อจัดการไฟล์ PDF และภาพปก
pdf_bucket = AsyncIOMotorGridFSBucket(database, bucket_name="pdfs")
cover_bucket = AsyncIOMotorGridFSBucket(database, bucket_name="covers")

# Use the regular collection for book metadata
from app.database import book_collection

AVAILABLE_CATEGORIES = [
    "ความรู้", "นิยาย", "มังงะ", "ศิลปะ", "วิทยาศาสตร์", 
    "ประวัติศาสตร์", "ธุรกิจ", "การศึกษา", "เทคโนโลยี", 
    "สุขภาพ", "การเงิน", "จิตวิทยา", "อื่นๆ"
]

class BookResponse(BaseModel): #สำหรับส่งข้อมูลหนังสือกลับไปยังลูกค้า
    id: str
    title: str
    author: str
    cover_id: Optional[str] = None  # GridFS file ID for cover
    pdf_id: Optional[str] = None    # GridFS file ID for PDF
    rating: float
    description: str
    category: str
    price: int = 0
    created_at: datetime
    file_size: Optional[int] = None
    has_pdf: bool = False
    has_cover: bool = False

class CategoryResponse(BaseModel): #สำหรับส่งรายการหมวดหมู่หนังสือ
    categories: List[str]

async def upload_file_to_gridfs(file: UploadFile, bucket: AsyncIOMotorGridFSBucket, file_type: str) -> tuple[ObjectId, int]:
    """Upload file to GridFS and return file ID and size"""
    try:
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size (MongoDB has practical limits)
        if file_type == "pdf":
            max_size = 100 * 1024 * 1024  # 100MB for PDFs
        else:  # cover image
            max_size = 5 * 1024 * 1024    # 5MB for images
            
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

async def download_file_from_gridfs(file_id: ObjectId, bucket: AsyncIOMotorGridFSBucket):
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

async def is_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role", "reader") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/categories", response_model=CategoryResponse) #เส้นทางสำหรับดึงรายการหมวดหมู่หนังสือ
async def get_categories(current_user: dict = Depends(get_current_user)):
    """Get all available book categories."""
    return CategoryResponse(categories=AVAILABLE_CATEGORIES)

@router.post("/", response_model=BookResponse) #เส้นทางสำหรับอัปโหลดหนังสือใหม่พร้อมไฟล์ปกและ PDF
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
    if category not in AVAILABLE_CATEGORIES: #ตรวจสอบว่าหมวดหมู่ที่ส่งมาถูกต้องหรือไม่
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
    } #ข้อมูลเมตาของหนังสือ เช่น ชื่อเรื่อง ผู้แต่ง คะแนน คำอธิบาย หมวดหมู่ ราคา วันที่สร้าง และผู้ที่อัปโหลด
    
    # Handle cover upload โคดส่วนนี้จะจัดการกับการอัปโหลดภาพปกหนังสือ
    cover_id = None
    if cover_file and cover_file.filename:
        # Validate cover file type
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
    
    # Handle PDF upload โค้ดส่วนนี้จะจัดการกับการอัปโหลดไฟล์ PDF ของหนังสือ
    pdf_id = None
    file_size = None
    if pdf_file and pdf_file.filename:
        # Validate PDF file
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
        
        return BookResponse(
            id=str(created_book["_id"]),
            title=created_book["title"],
            author=created_book["author"],
            cover_id=str(created_book["cover_id"]) if created_book.get("cover_id") else None,
            pdf_id=str(created_book["pdf_id"]) if created_book.get("pdf_id") else None,
            rating=created_book["rating"],
            description=created_book["description"],
            category=created_book.get("category", "อื่nๆ"),
            price=created_book.get("price", 0),
            created_at=created_book["created_at"],
            file_size=created_book.get("file_size"),
            has_pdf=bool(created_book.get("pdf_id")),
            has_cover=bool(created_book.get("cover_id"))
        )
        
    except Exception as e: #ถ้ามีข้อผิดพลาดเกิดขึ้นระหว่างการแทรกข้อมูลหนังสือลงในฐานข้อมูล จะส่ง HTTPException พร้อมรายละเอียดข้อผิดพลาด
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{book_id}/cover") #เส้นทางสำหรับดึงภาพปกหนังสือจาก GridFS
async def get_book_cover(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get book cover image from GridFS."""
    try:
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid book ID format")
            
        # Get book metadata
        book = await book_collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
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

@router.get("/{book_id}/read") #เส้นทางสำหรับอ่านหนังสือ (สตรีม PDF) จาก GridFS
async def read_book(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Stream PDF for reading from GridFS."""
    try:
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid book ID format")
            
        # Get book metadata
        book = await book_collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
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

@router.get("/{book_id}/download") #เส้นทางสำหรับดาวน์โหลดไฟล์ PDF ของหนังสือจาก GridFS
async def download_book(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Download PDF file from GridFS."""
    try:
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid book ID format")
            
        book = await book_collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
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

@router.get("/{book_id}", response_model=BookResponse) #เส้นทางสำหรับดึงรายละเอียดของหนังสือโดยใช้ ID ของหนังสือ
async def get_book_detail(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get details of a specific book by ID."""
    try:
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid book ID format")
            
        book = await book_collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
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

@router.get("/", response_model=list[BookResponse]) #เส้นทางสำหรับดึงรายการหนังสือทั้งหมดพร้อมการแบ่งหน้า การกรอง และการค้นหา
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

@router.delete("/{book_id}") #เส้นทางสำหรับลบหนังสือและไฟล์ที่เกี่ยวข้องออกจาก GridFS
async def delete_book(
    book_id: str,
    current_user: dict = Depends(is_admin)
):
    """Delete a book and its associated files from GridFS."""
    try:
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid book ID format")
            
        # Get book to find associated file IDs
        book = await book_collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
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

@router.get("/stats/storage") #เส้นทางสำหรับดึงสถิติการจัดเก็บไฟล์ใน GridFS
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