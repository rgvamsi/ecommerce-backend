from datetime import datetime, timezone
from fastapi import HTTPException, status
from bson import ObjectId
from app.services.database import products_collection
from app.utils.helper import product_helper
from app.models.products_model import Product,ProductInDB
class ProductManager:
    def __init__(self):
        self.collection = products_collection  # Reference to the products collection

    def create_product(self, product):
        try:
            # Check if the the product already exists
            if self.collection.find_one({"image": product.image}):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Product is already existed"
                )
            product_data = product.dict()
            product_data["created_at"] = datetime.now(timezone.utc)
            product_data["updated_at"] = datetime.now(timezone.utc)
            result = self.collection.insert_one(product_data)
            product_data["id"] = str(result.inserted_id)
            return product_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def list_products(self, pagination_token=0,limit=20):
        try:
            products_cursor = self.collection.find({}).skip(pagination_token).limit(limit)
            products = products_cursor.to_list(length=limit)
            response = {
            "products": [product_helper(product) for product in products],
            "next_token": pagination_token + limit if len(products) > limit else None
            }
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def get_product(self, product_id: str):
        try:
            product = self.collection.find_one({"_id": ObjectId(product_id)})
            if product:
                return product_helper(product)
            raise HTTPException(status_code=404, detail="Product not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def update_product(self, product_id: str, product_data):
        try:
            update_data = product_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.now(timezone.utc)
            update_result = self.collection.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_data}
            )
            if update_result.modified_count == 0:
                raise HTTPException(status_code=404, detail="Product not found")
            return  {"detail": "User updated successfully."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def delete_product(self, product_id: str):
        try:
            delete_result = self.collection.delete_one({"_id": ObjectId(product_id)})
            if delete_result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Product not found")
            return {"detail": "Product deleted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))