from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransactionBase(BaseModel):
    userId: str
    type: str  # topup / purchase / rent
    amount: float
    points: int
    bookId: Optional[str] = None
    status: str = "pending"

class TransactionCreate(TransactionBase):
    pass

class TransactionInDB(TransactionBase):
    transactionId: str
    createdAt: datetime