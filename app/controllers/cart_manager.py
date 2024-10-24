from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.services.database import cart_collection

class CartManager:
    def __init__(self) -> None:
        self.collection=cart_collection
    def add_product_to_cart(self,item,user_email):
        try:
            product_id = item.product_id
            quantity = item.quantity

            # Find the user's existing cart
            cart = self.collection.find_one({"user_email": user_email})

            if cart:
                # Check if the product already exists in the cart
                product_found = False  # Flag to track if product is found

                for cart_item in cart["items"]:
                    if cart_item["product_id"] == product_id:
                        # Update the quantity of the existing product
                        cart_item["quantity"] += quantity
                        product_found = True
                        break  # Stop the loop if product is found

                if not product_found:
                    # If product does not exist, add it to the cart
                    cart["items"].append({"product_id": product_id, "quantity": quantity})

                # Update the cart's updated_at timestamp
                cart["updated_at"] = datetime.now(timezone.utc)
                self.collection.update_one({"_id": cart["_id"]}, {"$set": cart})
                return {"message": "Cart updated successfully"}

            # If no cart exists, create a new one for the user
            new_cart = {
                "user_email": user_email,
                "items": [{"product_id": product_id, "quantity": quantity}],
                "updated_at": datetime.now(timezone.utc)
            }
            self.collection.insert_one(new_cart)
            return {"message": "New cart created and product added successfully"}

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def remove_from_cart(self,product_id,user_email):
        try:
            # Find the user's cart
            cart = self.collection.find_one({"user_email": user_email})
            if not cart:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

            # Filter out the product to remove it
            new_items = [item for item in cart["items"] if item["product_id"] != product_id]
            cart["items"] = new_items
            cart["updated_at"] = datetime.now(timezone.utc)
            cart_collection.update_one({"_id": cart["_id"]}, {"$set": cart})

            return {"message": "Product removed from cart successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def update_cart(self,product,product_id,user_email):
        try:
            # Find the user's cart
            cart = cart_collection.find_one({"user_email": user_email})
            if not cart:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
                )

            # Check if the product exists in the cart
            product_found = False
            for item in cart["items"]:
                if item["product_id"] == product_id:
                    item["quantity"] = product.quantity  # Update quantity
                    product_found = True
                    break

            if not product_found:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found in cart",
                )

            # Update the cart in the database
            cart["updated_at"] = datetime.now(timezone.utc)
            cart_collection.update_one({"_id": cart["_id"]}, {"$set": cart})

            return {"message": "Product quantity updated successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def view_cart(self,user_email):
        # Find the user's cart
        cart = cart_collection.find_one({"user_email": user_email})
        if not cart:
            return {"message": "Cart is empty", "items": []}

        return {"items": cart["items"], "updated_at": cart["updated_at"]}