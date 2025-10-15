import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel

from app.auth.jwt_handler import get_current_user
from app.database import book_collection, user_collection
from app.schemas.user import UserResponse
from app.utils.password import verify_password

# Initialize router
router = APIRouter(prefix="/users", tags=["Users"])

# ============ MODELS ============

class BookPurchase(BaseModel):
    book_id: str

class UserLibraryBook(BaseModel):
    book_id: str
    title: str
    author: str
    price_paid: int
    purchase_date: datetime
    has_pdf: bool
    has_cover: bool

class UserLibraryResponse(BaseModel):
    books: List[UserLibraryBook]
    total_books: int
    total_spent: int

class PointsRequest(BaseModel):
    points_to_add: int

class UserSettings(BaseModel):
    readingModeScroll: bool = True
    darkModeOption: str = "dark"  # "light", "dark", "system"
    notifications: bool = True
    autoSave: bool = True

class SettingUpdate(BaseModel):
    value: Any

class TrueMoneyPayment(BaseModel):
    voucher: str  # Voucher hash or URL

class ReadingActivity(BaseModel):
    book_id: str

class UserProfileUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None

class UsernameChangeRequest(BaseModel):
    new_username: str
    current_password: str

class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    country: Optional[str]
    phone: Optional[str]
    role: str
    points: int
    created_at: datetime
    updated_at: datetime

# ============ HELPER FUNCTIONS ============

async def get_user_by_username(username: str) -> Dict:
    """Get user document from database"""
    user = await user_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_book_by_id(book_id: str) -> Dict:
    """Get book document from database"""
    if not ObjectId.is_valid(book_id):
        raise HTTPException(status_code=400, detail="Invalid book ID format")
    
    book = await book_collection.find_one({"_id": ObjectId(book_id)})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

def extract_voucher_hash(voucher: str) -> str:
    """Extract voucher hash from URL if it's a full URL"""
    if "gift.truemoney.com" not in voucher:
        return voucher
    
    if "?v=" in voucher:
        return voucher.split("?v=")[1]
    elif "/campaign/" in voucher:
        voucher_hash = voucher.split("/campaign/")[1].rstrip("/")
        if "?v=" in voucher_hash:
            voucher_hash = voucher_hash.split("?v=")[1]
        return voucher_hash
    
    return voucher

async def validate_username_available(username: str) -> bool:
    """Check if username is available (not taken)"""
    existing_user = await user_collection.find_one({"username": username})
    return existing_user is None

async def verify_password(stored_password_hash: str, provided_password: str) -> bool:
    """Verify password against stored hash"""
    from app.auth.jwt_handler import verify_password as jwt_verify
    return jwt_verify(provided_password, stored_password_hash)

# ============ CORS OPTIONS HANDLERS ============

@router.options("/me/points")
async def options_points():
    return Response(status_code=200)

@router.options("/me/settings")
async def options_settings():
    return Response(status_code=200)

@router.options("/me/settings/{setting_key}")
async def options_single_setting(setting_key: str):
    return Response(status_code=200)

@router.options("/me/payment/truemoney")
async def options_truemoney_payment():
    return Response(status_code=200)

@router.options("/me/purchase/book")
async def options_purchase_book():
    return Response(status_code=200)

@router.options("/me/profile")
async def options_profile():
    return Response(status_code=200)

@router.options("/me/username")
async def options_username():
    return Response(status_code=200)

# ============ USER PROFILE ENDPOINTS ============

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information including points"""
    user = await get_user_by_username(current_user["username"])
    
    return UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        role=user.get("role", "reader"),
        points=user.get("points", 0),
        settings=user.get("settings", {})
    )

@router.patch("/me/points")
async def update_user_points(
    request: PointsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Add points to current user"""
    # Validate input
    if request.points_to_add <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Points to add must be greater than 0"
        )
    
    # Update user points
    result = await user_collection.update_one(
        {"username": current_user["username"]},
        {"$inc": {"points": request.points_to_add}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return updated user info
    user = await get_user_by_username(current_user["username"])
    return {
        "points": user.get("points", 0), 
        "message": f"Added {request.points_to_add} points successfully"
    }

# ============ USER SETTINGS ENDPOINTS ============

@router.get("/me/settings")
async def get_user_settings(current_user: dict = Depends(get_current_user)):
    """Get user settings"""
    user = await get_user_by_username(current_user["username"])
    
    # Default settings if none exist
    default_settings = {
        "readingModeScroll": True,
        "darkModeOption": "dark",
        "notifications": True,
        "autoSave": True
    }
    
    settings = user.get("settings", default_settings)
    return {"settings": settings}

@router.patch("/me/settings")
async def update_user_settings(
    settings: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update user settings (bulk update)"""
    # Validate settings keys
    allowed_keys = {"readingModeScroll", "darkModeOption", "notifications", "autoSave"}
    
    # Filter out invalid keys
    filtered_settings = {k: v for k, v in settings.items() if k in allowed_keys}
    
    if not filtered_settings:
        raise HTTPException(status_code=400, detail="No valid settings provided")
    
    # Update settings in database
    result = await user_collection.update_one(
        {"username": current_user["username"]},
        {"$set": {f"settings.{k}": v for k, v in filtered_settings.items()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get updated settings
    user = await get_user_by_username(current_user["username"])
    return {
        "message": "Settings updated successfully",
        "settings": user.get("settings", {})
    }

@router.patch("/me/settings/{setting_key}")
async def update_single_setting(
    setting_key: str,
    setting_update: SettingUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a single setting"""
    # Validate setting key
    allowed_keys = {"readingModeScroll", "darkModeOption", "notifications", "autoSave"}
    
    if setting_key not in allowed_keys:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid setting key. Allowed: {allowed_keys}"
        )
    
    # Validate darkModeOption values
    if setting_key == "darkModeOption" and setting_update.value not in ["light", "dark", "system"]:
        raise HTTPException(
            status_code=400, 
            detail="darkModeOption must be 'light', 'dark', or 'system'"
        )
    
    # Update single setting
    result = await user_collection.update_one(
        {"username": current_user["username"]},
        {"$set": {f"settings.{setting_key}": setting_update.value}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "message": f"Setting '{setting_key}' updated successfully",
        "setting": {setting_key: setting_update.value}
    }

# ============ PAYMENT ENDPOINTS ============

@router.post("/me/payment/truemoney")
async def process_truemoney_payment(
    payment: TrueMoneyPayment,
    current_user: dict = Depends(get_current_user)
):
    """Process TrueMoney wallet payment and add points to user"""
    # Fixed phone number
    FIXED_PHONE = "0966680754"
    
    # Extract voucher hash from URL if it's a full URL
    voucher_hash = extract_voucher_hash(payment.voucher)
    
    try:
        # Call TrueMoney API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://apiv2.hosting-ovezx.cloud/api_tmw",
                headers={"Content-Type": "application/json"},
                json={
                    "voucher": voucher_hash,
                    "phone": FIXED_PHONE
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, 
                    detail="Payment processing failed"
                )
            
            result = response.json()
            
            # Check if payment was successful
            if result.get("status", {}).get("code") != "SUCCESS":
                error_message = result.get("status", {}).get("message", "Payment failed")
                raise HTTPException(status_code=400, detail=error_message)
            
            # Extract payment amount
            voucher_data = result.get("data", {}).get("voucher", {})
            amount_baht = float(voucher_data.get("amount_baht", 0))
            
            # Convert baht to points (1 baht = 10 points)
            points_to_add = int(amount_baht * 10)
            
            # Add points to user account
            update_result = await user_collection.update_one(
                {"username": current_user["username"]},
                {
                    "$inc": {"points": points_to_add},
                    "$push": {
                        "payment_history": {
                            "type": "truemoney",
                            "voucher_id": voucher_data.get("voucher_id"),
                            "amount_baht": amount_baht,
                            "points_added": points_to_add,
                            "phone": FIXED_PHONE,
                            "timestamp": datetime.utcnow(),
                            "status": "success"
                        }
                    }
                }
            )
            
            if update_result.modified_count == 0:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get updated user info
            updated_user = await get_user_by_username(current_user["username"])
            
            return {
                "success": True,
                "message": f"Payment successful! Added {points_to_add} points",
                "payment_details": {
                    "amount_baht": amount_baht,
                    "points_added": points_to_add,
                    "voucher_id": voucher_data.get("voucher_id"),
                    "total_points": updated_user.get("points", 0)
                },
                "voucher_info": voucher_data
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Payment request timeout")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Payment service unavailable")
    except HTTPException:
        # Re-raise HTTPExceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/me/payment/history")
async def get_payment_history(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """Get user's payment history"""
    user = await get_user_by_username(current_user["username"])
    
    # Get payment history from user document
    payment_history = user.get("payment_history", [])
    
    # Sort by timestamp (newest first) and apply pagination
    sorted_history = sorted(
        payment_history, 
        key=lambda x: x.get("timestamp", datetime.min), 
        reverse=True
    )
    paginated_history = sorted_history[skip:skip + limit]
    
    # Format the response
    formatted_history = []
    for payment in paginated_history:
        formatted_payment = {
            "id": str(payment.get("voucher_id", "")),
            "type": payment.get("type", "unknown"),
            "amount_baht": payment.get("amount_baht", 0),
            "points_added": payment.get("points_added", 0),
            "phone": payment.get("phone", ""),
            "timestamp": payment.get("timestamp"),
            "status": payment.get("status", "unknown"),
            "created_at": payment.get("timestamp").strftime("%Y-%m-%d %H:%M:%S") if payment.get("timestamp") else None
        }
        formatted_history.append(formatted_payment)
    
    return {
        "history": formatted_history,
        "total_records": len(payment_history),
        "current_page": skip // limit + 1,
        "has_more": skip + limit < len(payment_history)
    }

# ============ BOOK PURCHASE ENDPOINTS ============

@router.post("/me/purchase/book")
async def purchase_book(
    book_purchase: BookPurchase,
    current_user: dict = Depends(get_current_user)
):
    """Purchase a book with user points"""
    # Get book details
    book = await get_book_by_id(book_purchase.book_id)
    
    # Get current user
    user = await get_user_by_username(current_user["username"])
    
    # Check if book is free
    book_price = book.get("price", 0)
    
    if book_price > 0:
        # Check if user has enough points
        user_points = user.get("points", 0)
        if user_points < book_price:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient points. Required: {book_price}, Available: {user_points}"
            )
    
    # Check if user already owns the book
    user_library = user.get("library", [])
    for book_entry in user_library:
        if str(book_entry.get("book_id")) == book_purchase.book_id:
            raise HTTPException(status_code=400, detail="Book already owned")
    
    # Prepare library entry
    library_entry = {
        "book_id": book_purchase.book_id,
        "title": book.get("title", ""),
        "author": book.get("author", ""),
        "price_paid": book_price,
        "purchase_date": datetime.utcnow(),
        "has_pdf": book.get("pdf_id") is not None,
        "has_cover": book.get("cover_id") is not None
    }
    
    # Update user record
    update_operations = {"$push": {"library": library_entry}}
    
    # Deduct points only if book is not free
    if book_price > 0:
        update_operations["$inc"] = {"points": -book_price}
    
    result = await user_collection.update_one(
        {"username": current_user["username"]},
        update_operations
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to purchase book")
    
    # Get updated user info
    updated_user = await get_user_by_username(current_user["username"])
    
    return {
        "success": True,
        "message": f"Successfully {'added' if book_price == 0 else 'purchased'} book: {book.get('title')}",
        "purchase_details": {
            "book_id": book_purchase.book_id,
            "book_title": book.get("title"),
            "price_paid": book_price,
            "remaining_points": updated_user.get("points", 0),
            "purchase_date": library_entry["purchase_date"]
        }
    }

@router.get("/me/library/check/{book_id}")
async def check_book_ownership(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Check if user owns a specific book"""
    # Validate book ID
    book = await get_book_by_id(book_id)
    
    # Get user
    user = await get_user_by_username(current_user["username"])
    
    # Check if book exists in user's library
    user_library = user.get("library", [])
    owned = False
    purchase_date = None
    
    for book_entry in user_library:
        if str(book_entry.get("book_id")) == book_id:
            owned = True
            purchase_date = book_entry.get("purchase_date")
            break
    
    return {
        "owned": owned,
        "purchase_date": purchase_date
    }

@router.get("/me/library", response_model=UserLibraryResponse)
async def get_user_library(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get user's library (purchased books)"""
    user = await get_user_by_username(current_user["username"])
    
    user_library = user.get("library", [])
    
    # Apply pagination
    total_books = len(user_library)
    paginated_library = user_library[skip:skip + limit]
    
    # Calculate total spent
    total_spent = sum(book.get("price_paid", 0) for book in user_library)
    
    # Convert to response format
    books = []
    for book_entry in paginated_library:
        books.append(UserLibraryBook(
            book_id=book_entry.get("book_id", ""),
            title=book_entry.get("title", ""),
            author=book_entry.get("author", ""),
            price_paid=book_entry.get("price_paid", 0),
            purchase_date=book_entry.get("purchase_date", datetime.utcnow()),
            has_pdf=book_entry.get("has_pdf", False),
            has_cover=book_entry.get("has_cover", False)
        ))
    
    return UserLibraryResponse(
        books=books,
        total_books=total_books,
        total_spent=total_spent
    )

@router.delete("/me/library/{book_id}")
async def remove_book_from_library(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove a book from user's library"""
    # Validate book ID
    await get_book_by_id(book_id)
    
    # Remove book from user's library
    result = await user_collection.update_one(
        {"username": current_user["username"]},
        {"$pull": {"library": {"book_id": book_id}}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Book not found in library")
    
    return {"message": "Book removed from library successfully"}

# ============ USER STATISTICS ENDPOINTS ============

@router.get("/me/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """Get user statistics"""
    user = await get_user_by_username(current_user["username"])
    
    user_library = user.get("library", [])
    payment_history = user.get("payment_history", [])
    
    # Calculate stats
    total_books = len(user_library)
    total_spent = sum(book.get("price_paid", 0) for book in user_library)
    total_payments = len(payment_history)
    total_points_purchased = sum(payment.get("points_added", 0) for payment in payment_history)
    
    return {
        "total_books_owned": total_books,
        "total_points_spent": total_spent,
        "total_payments": total_payments,
        "total_points_purchased": total_points_purchased,
        "current_points": user.get("points", 0),
        "account_created": user.get("created_at", datetime.utcnow()),
        "last_purchase": user_library[-1].get("purchase_date") if user_library else None,
        "favorite_categories": []  # You can implement category analysis later
    }

# ============ READING ACTIVITY ENDPOINTS ============

@router.post("/me/reading")
async def log_reading_activity(
    activity: ReadingActivity,
    current_user: dict = Depends(get_current_user)
):
    """
    Log a reading activity for the current user.
    If the book already exists in reading_history → update last_read & increment read_count.
    Otherwise → add new record.
    """
    # Get book info
    book = await get_book_by_id(activity.book_id)
    
    # Prepare reading record
    reading_entry = {
        "book_id": str(book["_id"]),
        "title": book.get("title", "Untitled"),
        "category": book.get("category", "อื่นๆ"),
        "last_read": datetime.utcnow(),
    }
    
    # Get user
    user = await get_user_by_username(current_user["username"])
    
    # Check if user already has history for this book
    existing_entry = None
    for item in user.get("reading_history", []):
        if item["book_id"] == str(book["_id"]):
            existing_entry = item
            break
    
    if existing_entry:
        # Update existing entry (increment read_count, update timestamp)
        await user_collection.update_one(
            {"username": current_user["username"], "reading_history.book_id": str(book["_id"])},
            {
                "$set": {"reading_history.$.last_read": datetime.utcnow()},
                "$inc": {"reading_history.$.read_count": 1}
            }
        )
    else:
        # Add new reading entry
        reading_entry["read_count"] = 1
        await user_collection.update_one(
            {"username": current_user["username"]},
            {"$push": {"reading_history": reading_entry}}
        )
    
    return {"success": True, "message": f"Reading activity logged for {book.get('title')}"}

@router.get("/me/reading/history")
async def get_reading_history(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50)
):
    """Get user's recent reading history"""
    user = await get_user_by_username(current_user["username"])
    
    history = user.get("reading_history", [])
    sorted_history = sorted(history, key=lambda x: x["last_read"], reverse=True)
    
    return {
        "history": sorted_history[:limit],
        "total_records": len(history)
    }

# ============ PROFILE ENDPOINTS ============

@router.get("/me/profile", response_model=UserProfileResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get full user profile information"""
    user = await get_user_by_username(current_user["username"])
    
    return UserProfileResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name", ""),
        bio=user.get("bio", ""),
        avatar_url=user.get("avatar_url", ""),
        country=user.get("country", ""),
        phone=user.get("phone", ""),
        role=user.get("role", "reader"),
        points=user.get("points", 0),
        created_at=user.get("created_at", datetime.utcnow()),
        updated_at=user.get("updated_at", datetime.utcnow())
    )

@router.patch("/me/profile")
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile information"""
    # Get user
    user = await get_user_by_username(current_user["username"])

    update_fields = {}
    for field, value in profile_update.dict(exclude_unset=True).items():
        if value is not None:
            update_fields[field] = value

    if not update_fields:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    update_fields["updated_at"] = datetime.utcnow()

    # Update user in database
    result = await user_collection.update_one(
        {"_id": user["_id"]},
        {"$set": update_fields}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update profile")

    updated_user = await get_user_by_username(current_user["username"])

    return {
        "message": "Profile updated successfully",
        "profile": {
            "id": str(updated_user["_id"]),
            "username": updated_user["username"],
            "email": updated_user.get("email"),
            "full_name": updated_user.get("full_name"),
            "bio": updated_user.get("bio"),
            "avatar_url": updated_user.get("avatar_url"),
            "country": updated_user.get("country"),
            "phone": updated_user.get("phone"),
            "role": updated_user.get("role", "reader"),
            "points": updated_user.get("points", 0),
            "created_at": updated_user.get("created_at"),
            "updated_at": updated_user.get("updated_at"),
        }
    }

@router.patch("/me/username")
async def change_username(
    username_request: UsernameChangeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Change user's username"""
    # Validate new username format
    if len(username_request.new_username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    
    if len(username_request.new_username) > 30:
        raise HTTPException(status_code=400, detail="Username must not exceed 30 characters")
    
    # Username can only contain alphanumeric and underscores
    if not username_request.new_username.replace("_", "").isalnum():
        raise HTTPException(
            status_code=400, 
            detail="Username can only contain letters, numbers, and underscores"
        )
    
    # Check if new username is same as current
    if username_request.new_username == current_user["username"]:
        raise HTTPException(status_code=400, detail="New username must be different from current")
    
    # Check if new username already exists
    username_available = await validate_username_available(username_request.new_username)
    if not username_available:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Get current user from database
    user = await user_collection.find_one({"username": current_user["username"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify password - ใช้ hashed_password แทน password
    stored_password_hash = user.get("hashed_password")
    if not stored_password_hash:
        raise HTTPException(status_code=500, detail="Password field not found in user record. Please contact support.")
    
    password_valid = verify_password(username_request.current_password, stored_password_hash)
    
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Update username
    result = await user_collection.update_one(
        {"username": current_user["username"]},
        {
            "$set": {
                "username": username_request.new_username,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to change username")
    
    # Get updated user
    updated_user = await user_collection.find_one({"username": username_request.new_username})
    
    return {
        "success": True,
        "message": f"Username changed successfully to {username_request.new_username}",
        "old_username": current_user["username"],
        "new_username": username_request.new_username,
        "user": UserProfileResponse(
            id=str(updated_user["_id"]),
            username=updated_user["username"],
            email=updated_user["email"],
            full_name=updated_user.get("full_name", ""),
            bio=updated_user.get("bio", ""),
            avatar_url=updated_user.get("avatar_url", ""),
            country=updated_user.get("country", ""),
            phone=updated_user.get("phone", ""),
            role=updated_user.get("role", "reader"),
            points=updated_user.get("points", 0),
            created_at=updated_user.get("created_at", datetime.utcnow()),
            updated_at=updated_user.get("updated_at", datetime.utcnow())
        )
    }

@router.get("/profile/{username}")
async def get_public_user_profile(
    username: str,
    current_user: dict = Depends(get_current_user)
):
    """Get public user profile (limited information)"""
    user = await get_user_by_username(username)
    
    # Return only public information
    return {
        "username": user["username"],
        "full_name": user.get("full_name", ""),
        "bio": user.get("bio", ""),
        "avatar_url": user.get("avatar_url", ""),
        "country": user.get("country", ""),
        "created_at": user.get("created_at"),
        "role": user.get("role", "reader")
    }