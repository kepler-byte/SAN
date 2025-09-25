import httpx
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import user_collection
from app.auth.jwt_handler import get_current_user
from app.schemas.user import UserResponse
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])

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

@router.patch("/me/points")
async def update_user_points(
    points_to_add: int, 
    current_user: dict = Depends(get_current_user)
):
    """Add points to current user"""
    result = await user_collection.update_one(
        {"username": current_user["username"]},
        {"$inc": {"points": points_to_add}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return updated user info
    user = await user_collection.find_one({"username": current_user["username"]})
    return {"points": user.get("points", 0), "message": f"Added {points_to_add} points"}

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