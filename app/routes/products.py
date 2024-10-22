from fastapi import APIRouter, HTTPException, status, Depends,Query
from typing import Dict
from app.models.products_model import Product,ProductInDB,ProductUpdateModel
from app.middleware.auth import get_current_user
from app.controllers.product_manager import ProductManager


router = APIRouter()
# Create an instance of ProductManager
product_manager = ProductManager()

@router.post("/products", response_model=ProductInDB, status_code=status.HTTP_201_CREATED)
def create_product(
    product: Product, current_user: dict = Depends(get_current_user)
):
    # Check if the logged-in user is an admin
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return product_manager.create_product(product)

@router.get("/products",response_model=Dict)
def list_products(pagination_token: int = Query(0),limit: int = 20,current_user: dict = Depends(get_current_user)):
    return product_manager.list_products(pagination_token=pagination_token,limit=limit)

@router.get("/products/{product_id}", response_model=ProductInDB)
def read_product(product_id: str,current_user: dict = Depends(get_current_user)):
    return product_manager.get_product(product_id)

@router.put("/products/{product_id}")
def update_product(product_id: str, product_data: ProductUpdateModel, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return product_manager.update_product(product_id, product_data)

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return product_manager.delete_product(product_id)