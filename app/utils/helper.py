from fastapi import HTTPException, status

def user_helper(user) -> dict:
    try:
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "role": user.get("role", "user"),  # Default role as 'user' if not found
            "firstname":user.get("firstname",""),
            "lastname":user.get("lastname",""),
            "created_at":user.get("created_at",""),
            "updated_at":user.get("updated_at","")
        }
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

def product_helper(product) -> dict:
    try:
        return {
            "id": str(product["_id"]),
            "name": product["name"],
            "description": product["description"],
            "price": product["price"] , 
            "stock":product.get("stock",""),
            "stock_status":product.get("stock_status",""),
            "image":product.get("image",""),
            "created_at":product.get("created_at",""),
            "updated_at":product.get("updated_at","")
        }
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
