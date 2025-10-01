import httpx
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from app.database import user_collection
from app.database import book_collection
from app.auth.jwt_handler import get_current_user
from app.schemas.user import UserResponse
from pydantic import BaseModel
from typing import Dict, Any, List
from bson import ObjectId

router = APIRouter(prefix="/users", tags=["Users"])

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

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information including points"""
    user = await user_collection.find_one({"username": current_user["username"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        role=user.get("role", "reader"),
        points=user.get("points", 0),
        settings=user.get("settings", {})
    )

# OPTIONS handlers for CORS
@router.options("/me/points")
async def options_points(points_to_add: int = Query(None)):
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

@router.patch("/me/points")
async def update_user_points(
    request: PointsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Add points to current user"""
    try:
        # ตรวจสอบว่า points_to_add เป็น positive number
        if request.points_to_add <= 0:
            raise HTTPException(
                status_code=400, 
                detail="Points to add must be greater than 0"
            )
        
        result = await user_collection.update_one(
            {"username": current_user["username"]},
            {"$inc": {"points": request.points_to_add}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Return updated user info
        user = await user_collection.find_one({"username": current_user["username"]})
        return {
            "points": user.get("points", 0), 
            "message": f"Added {request.points_to_add} points successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_user_points: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while updating points"
        )

class UserSettings(BaseModel):
    readingModeScroll: bool = True
    darkModeOption: str = "dark"  # "light", "dark", "system"
    notifications: bool = True
    autoSave: bool = True

class SettingUpdate(BaseModel):
    value: Any

@router.get("/me/settings")
async def get_user_settings(current_user: dict = Depends(get_current_user)):
    """Get user settings"""
    user = await user_collection.find_one({"username": current_user["username"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
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
    user = await user_collection.find_one({"username": current_user["username"]})
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
        raise HTTPException(status_code=400, detail=f"Invalid setting key. Allowed: {allowed_keys}")
    
    # Validate darkModeOption values
    if setting_key == "darkModeOption" and setting_update.value not in ["light", "dark", "system"]:
        raise HTTPException(status_code=400, detail="darkModeOption must be 'light', 'dark', or 'system'")
    
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

class TrueMoneyPayment(BaseModel):
    voucher: str
    # phone is now fixed, no need to accept it from user

@router.post("/me/payment/truemoney")
async def process_truemoney_payment(
    payment: TrueMoneyPayment,
    current_user: dict = Depends(get_current_user)
):
    """Process TrueMoney wallet payment and add points to user"""
    
    # Fixed phone number
    FIXED_PHONE = "0966680754"
    
    # Extract voucher hash from URL if it's a full URL
    voucher_hash = payment.voucher
    if "gift.truemoney.com" in voucher_hash:
        if "?v=" in voucher_hash:
            voucher_hash = voucher_hash.split("?v=")[1]
        elif "/campaign/" in voucher_hash:
            voucher_hash = voucher_hash.split("/campaign/")[1].rstrip("/")
            if "?v=" in voucher_hash:
                voucher_hash = voucher_hash.split("?v=")[1]
    
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
            updated_user = await user_collection.find_one({"username": current_user["username"]})
            
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
    limit: int = 20,  # Number of records to return
    skip: int = 0     # Number of records to skip (for pagination)
):
    """Get user's payment history"""
    user = await user_collection.find_one({"username": current_user["username"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get payment history from user document
    payment_history = user.get("payment_history", [])
    
    # Sort by timestamp (newest first) and apply pagination
    sorted_history = sorted(payment_history, key=lambda x: x.get("timestamp", datetime.min), reverse=True)
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

@router.post("/me/purchase/book")
async def purchase_book(
    book_purchase: BookPurchase,
    current_user: dict = Depends(get_current_user)
):
    """Purchase a book with user points"""
    try:
        # Validate book ID
        if not ObjectId.is_valid(book_purchase.book_id):
            raise HTTPException(status_code=400, detail="Invalid book ID format")
        
        # Get book details
        book = await book_collection.find_one({"_id": ObjectId(book_purchase.book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Get current user
        user = await user_collection.find_one({"username": current_user["username"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if book is free
        book_price = book.get("price", 0)
        if book_price == 0:
            # Free book - just add to library without deducting points
            pass
        else:
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
        update_operations = {
            "$push": {"library": library_entry}
        }
        
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
        updated_user = await user_collection.find_one({"username": current_user["username"]})
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/me/library/check/{book_id}")
async def check_book_ownership(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Check if user owns a specific book"""
    try:
        # Validate book ID
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid book ID format")
        
        # Get user
        user = await user_collection.find_one({"username": current_user["username"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/me/library", response_model=UserLibraryResponse)
async def get_user_library(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get user's library (purchased books)"""
    try:
        user = await user_collection.find_one({"username": current_user["username"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/me/library/{book_id}")
async def remove_book_from_library(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove a book from user's library"""
    try:
        # Validate book ID
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid book ID format")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/me/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """Get user statistics"""
    try:
        user = await user_collection.find_one({"username": current_user["username"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")