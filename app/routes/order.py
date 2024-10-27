from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware.auth import get_current_user
from app.models.order_model import OrderResponse, CreateOrderRequest
from app.controllers.order_manager import OrderManager


router = APIRouter()
# Create an instance of ProductManager
order_manager = OrderManager()


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    order_request: CreateOrderRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Extract user details from the token
        user_email = current_user["email"]
        return order_manager.place_order(order_request,user_email)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

@router.get("/orders", response_model=List[OrderResponse],status_code=status.HTTP_200_OK)
def get_order_history(current_user: dict = Depends(get_current_user)):
    try:
        # Extract user details from the token
        user_email = current_user["email"]
        return order_manager.get_order_history(user_email)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )  from e
