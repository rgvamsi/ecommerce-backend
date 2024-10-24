from typing import List
from pydantic import BaseModel,Field

class CartItem(BaseModel):
    product_id: str  # ObjectId in MongoDB is stored as a string
    quantity: int =Field(..., ge=0, description="quantity must be a positive integer")

class Cart(BaseModel):
    user_email: str
    items: List[CartItem] = []

class CartUpdateItem(BaseModel):
    quantity: int =Field(..., ge=0, description="quantity must be a positive integer")
