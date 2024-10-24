from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.cart_model import CartItem,CartUpdateItem
from app.middleware.auth import get_current_user
from app.controllers.cart_manager import CartManager


router = APIRouter()
# Create an instance of ProductManager
cart_manager = CartManager()

@router.post("/cart",status_code=status.HTTP_201_CREATED)
def add_to_cart(item: CartItem, current_user: dict = Depends(get_current_user)):
    try:
        # Check if the product_id is a valid ObjectId
        if not ObjectId.is_valid(item.product_id):
            raise ValueError("Invalid product_id format")
        user_email = current_user["email"]
        return cart_manager.add_product_to_cart(item,user_email)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/cart/{product_id}")
def remove_from_cart(product_id: str, user: dict = Depends(get_current_user)):
    try:
        user_email = user["email"]
        return cart_manager.remove_from_cart(product_id,user_email)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/cart/{product_id}")
def update_cart(product:CartUpdateItem,product_id: str,
    user: dict = Depends(get_current_user)):
    try:
        user_email = user["email"]
        return cart_manager.update_cart(product,product_id,user_email)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/cart")
def view_cart(user: dict = Depends(get_current_user)):
    try:
        user_email = user["email"]
        return cart_manager.view_cart(user_email)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))