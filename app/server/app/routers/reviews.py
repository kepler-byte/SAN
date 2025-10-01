from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from app.database import book_collection, user_collection
from app.auth.jwt_handler import get_current_user

router = APIRouter(prefix="/books", tags=["Reviews"])

# Pydantic Models
class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    review_text: str = Field(..., min_length=10, max_length=2000)

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = Field(None, min_length=10, max_length=2000)

class ReviewResponse(BaseModel):
    review_id: str
    user_id: str
    username: str
    rating: int
    review_text: str
    created_at: datetime
    updated_at: datetime
    is_owner: bool = False

class BookReviewsResponse(BaseModel):
    book_id: str
    book_title: str
    total_reviews: int
    average_rating: float
    reviews: List[ReviewResponse]

# Helper function to check if user owns the book
async def check_book_ownership(book_id: str, username: str) -> bool:
    user = await user_collection.find_one({"username": username})
    if not user:
        return False
    
    user_library = user.get("library", [])
    for book_entry in user_library:
        if str(book_entry.get("book_id")) == book_id:
            return True
    return False

# Helper function to check if book is free
async def is_book_free(book_id: str) -> bool:
    book = await book_collection.find_one({"_id": ObjectId(book_id)})
    if not book:
        return False
    return book.get("price", 0) == 0

@router.post("/{book_id}/reviews", response_model=ReviewResponse)
async def create_review(
    book_id: str,
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new review for a book (must own the book or book must be free)"""
    try:
        # Validate book ID
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid book ID format")
        
        # Check if book exists
        book = await book_collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Check if user owns the book or if book is free
        owns_book = await check_book_ownership(book_id, current_user["username"])
        book_is_free = await is_book_free(book_id)
        
        if not owns_book and not book_is_free:
            raise HTTPException(
                status_code=403, 
                detail="You must own this book to review it"
            )
        
        # Check if user already reviewed this book
        existing_reviews = book.get("reviews", [])
        for rev in existing_reviews:
            if rev.get("user_id") == current_user["username"]:
                raise HTTPException(
                    status_code=400, 
                    detail="You have already reviewed this book. Use PATCH to update your review."
                )
        
        # Create review
        review_id = str(ObjectId())
        new_review = {
            "review_id": review_id,
            "user_id": current_user["username"],
            "username": current_user["username"],
            "rating": review.rating,
            "review_text": review.review_text,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Add review to book
        result = await book_collection.update_one(
            {"_id": ObjectId(book_id)},
            {
                "$push": {"reviews": new_review},
                "$inc": {"review_count": 1}
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to create review")
        
        # Update book's average rating
        updated_book = await book_collection.find_one({"_id": ObjectId(book_id)})
        all_reviews = updated_book.get("reviews", [])
        if all_reviews:
            avg_rating = sum(r["rating"] for r in all_reviews) / len(all_reviews)
            await book_collection.update_one(
                {"_id": ObjectId(book_id)},
                {"$set": {"rating": round(avg_rating, 1)}}
            )
        
        return ReviewResponse(
            review_id=review_id,
            user_id=current_user["username"],
            username=current_user["username"],
            rating=review.rating,
            review_text=review.review_text,
            created_at=new_review["created_at"],
            updated_at=new_review["updated_at"],
            is_owner=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{book_id}/reviews", response_model=BookReviewsResponse)
async def get_book_reviews(
    book_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get all reviews for a specific book"""
    try:
        # Validate book ID
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid book ID format")
        
        # Get book
        book = await book_collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Get reviews
        all_reviews = book.get("reviews", [])
        
        # Sort by created_at (newest first)
        sorted_reviews = sorted(
            all_reviews, 
            key=lambda x: x.get("created_at", datetime.min), 
            reverse=True
        )
        
        # Apply pagination
        paginated_reviews = sorted_reviews[skip:skip + limit]
        
        # Calculate average rating
        avg_rating = 0.0
        if all_reviews:
            avg_rating = sum(r["rating"] for r in all_reviews) / len(all_reviews)
        
        # Format reviews
        formatted_reviews = []
        for rev in paginated_reviews:
            formatted_reviews.append(ReviewResponse(
                review_id=rev.get("review_id", ""),
                user_id=rev.get("user_id", ""),
                username=rev.get("username", "Anonymous"),
                rating=rev.get("rating", 0),
                review_text=rev.get("review_text", ""),
                created_at=rev.get("created_at", datetime.utcnow()),
                updated_at=rev.get("updated_at", datetime.utcnow()),
                is_owner=(rev.get("user_id") == current_user["username"])
            ))
        
        return BookReviewsResponse(
            book_id=book_id,
            book_title=book.get("title", ""),
            total_reviews=len(all_reviews),
            average_rating=round(avg_rating, 1),
            reviews=formatted_reviews
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.patch("/{book_id}/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    book_id: str,
    review_id: str,
    review_update: ReviewUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user's own review"""
    try:
        # Validate book ID
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid book ID format")
        
        # Get book
        book = await book_collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Find the review
        reviews = book.get("reviews", [])
        review_index = None
        review_data = None
        
        for idx, rev in enumerate(reviews):
            if rev.get("review_id") == review_id:
                review_index = idx
                review_data = rev
                break
        
        if review_data is None:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Check ownership
        if review_data.get("user_id") != current_user["username"]:
            raise HTTPException(
                status_code=403, 
                detail="You can only update your own reviews"
            )
        
        # Update review fields
        if review_update.rating is not None:
            review_data["rating"] = review_update.rating
        if review_update.review_text is not None:
            review_data["review_text"] = review_update.review_text
        
        review_data["updated_at"] = datetime.utcnow()
        
        # Update in database
        reviews[review_index] = review_data
        result = await book_collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": {"reviews": reviews}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update review")
        
        # Recalculate average rating
        avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
        await book_collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": {"rating": round(avg_rating, 1)}}
        )
        
        return ReviewResponse(
            review_id=review_data["review_id"],
            user_id=review_data["user_id"],
            username=review_data["username"],
            rating=review_data["rating"],
            review_text=review_data["review_text"],
            created_at=review_data["created_at"],
            updated_at=review_data["updated_at"],
            is_owner=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{book_id}/reviews/{review_id}")
async def delete_review(
    book_id: str,
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete user's own review"""
    try:
        # Validate book ID
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid book ID format")
        
        # Get book
        book = await book_collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Find and verify ownership
        reviews = book.get("reviews", [])
        review_to_delete = None
        
        for rev in reviews:
            if rev.get("review_id") == review_id:
                review_to_delete = rev
                break
        
        if review_to_delete is None:
            raise HTTPException(status_code=404, detail="Review not found")
        
        if review_to_delete.get("user_id") != current_user["username"]:
            raise HTTPException(
                status_code=403, 
                detail="You can only delete your own reviews"
            )
        
        # Remove review
        result = await book_collection.update_one(
            {"_id": ObjectId(book_id)},
            {
                "$pull": {"reviews": {"review_id": review_id}},
                "$inc": {"review_count": -1}
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete review")
        
        # Recalculate average rating
        updated_book = await book_collection.find_one({"_id": ObjectId(book_id)})
        remaining_reviews = updated_book.get("reviews", [])
        
        if remaining_reviews:
            avg_rating = sum(r["rating"] for r in remaining_reviews) / len(remaining_reviews)
            await book_collection.update_one(
                {"_id": ObjectId(book_id)},
                {"$set": {"rating": round(avg_rating, 1)}}
            )
        else:
            # No reviews left, set default rating
            await book_collection.update_one(
                {"_id": ObjectId(book_id)},
                {"$set": {"rating": 0}}
            )
        
        return {"message": "Review deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/user/reviews")
async def get_user_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get all reviews written by the current user"""
    try:
        # Find all books with reviews from this user
        books_with_reviews = await book_collection.find(
            {"reviews.user_id": current_user["username"]}
        ).to_list(length=None)
        
        user_reviews = []
        for book in books_with_reviews:
            for review in book.get("reviews", []):
                if review.get("user_id") == current_user["username"]:
                    user_reviews.append({
                        "book_id": str(book["_id"]),
                        "book_title": book.get("title", ""),
                        "book_author": book.get("author", ""),
                        "review": ReviewResponse(
                            review_id=review.get("review_id", ""),
                            user_id=review.get("user_id", ""),
                            username=review.get("username", ""),
                            rating=review.get("rating", 0),
                            review_text=review.get("review_text", ""),
                            created_at=review.get("created_at", datetime.utcnow()),
                            updated_at=review.get("updated_at", datetime.utcnow()),
                            is_owner=True
                        )
                    })
        
        # Sort by created_at (newest first)
        user_reviews.sort(key=lambda x: x["review"]["created_at"], reverse=True)
        
        # Apply pagination
        paginated_reviews = user_reviews[skip:skip + limit]
        
        return {
            "total_reviews": len(user_reviews),
            "reviews": paginated_reviews
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")