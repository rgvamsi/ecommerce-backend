from typing import List
from datetime import datetime
from pydantic import BaseModel

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class CreateOrderRequest(BaseModel):
    items: List[OrderItem]
    address: str

class OrderResponse(BaseModel):
    order_id: str
    user_email: str
    items: List[OrderItem]
    total_amount: float
    address: str
    created_at: datetime
