from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.services.database import order_collection


class OrderManager:
    def __init__(self) -> None:
        self.collection=order_collection
    def place_order(self,order_request,user_email):
        try:
            # Calculate total amount
            total_amount=0
            for item in order_request.items:
                total_amount += item.price * item.quantity
            order_data = {
                "user_email": user_email,
                "items": [item.dict() for item in order_request.items],
                "total_amount": total_amount,
                "address": order_request.address,
                "created_at": datetime.now(timezone.utc),
            }

            result = self.collection.insert_one(order_data)
            if not result.inserted_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to place order",
                )

            # Return the order details
            return {
                "order_id": str(result.inserted_id),
                "user_email": user_email,
                "items": order_request.items,
                "total_amount": total_amount,
                "address": order_request.address,
                "created_at": order_data["created_at"]
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
    def get_order_history(self,user_email):
        try:
            # Fetch the user's orders from the database
            orders = self.collection.find({"user_email": user_email})

            # Format the orders for the response
            order_list = []
            for order in orders:
                order_list.append({
                    "order_id": str(order["_id"]),
                    "user_email": order["user_email"],
                    "items": order["items"],
                    "total_amount": order["total_amount"],
                    "address": order["address"],
                    "created_at": order["created_at"].isoformat(),
                })

            if not order_list:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No orders found for the user",
                )

            return order_list
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
