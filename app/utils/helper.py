from bson import ObjectId

def user_helper(user) -> dict:
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