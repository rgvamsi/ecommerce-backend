import jwt
import os
# from typing import List
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import users_collection, User, UserLogin, refresh_tokens_collection,UserUpdateModel
from app.auth import get_password_hash,create_access_token, verify_password, get_current_user,create_refresh_token
from datetime import datetime, timedelta, timezone
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter()

@router.post("/users/signup",status_code=status.HTTP_201_CREATED)
def signup(user: User):
    try:
        # Check if the email already exists
        if users_collection.find_one({"email": user.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email already registered"
            )
        hashed_password = get_password_hash(user.password)

        # Create new user object with timestamps
        new_user = user.model_dump()
        new_user["password"] = hashed_password
        new_user["created_at"] = datetime.now(timezone.utc)  # Set creation timestamp
        new_user["updated_at"] = datetime.now(timezone.utc)  # Set update timestamp
        result = users_collection.insert_one(new_user)

        return {"id": str(result.inserted_id), "message": "User registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@router.post("/users/login")
def login(user_login: UserLogin):  # Use the new UserLogin model
    try:
        db_user = users_collection.find_one({"email": user_login.email})
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if not verify_password(user_login.password, db_user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        access_token = create_access_token(data={"sub": user_login.email})
        refresh_token = create_refresh_token(data={"sub": user_login.email})

        # Store the refresh token in the database
        refresh_tokens_collection.insert_one({
            "user_id": str(db_user["_id"]),
            "token": refresh_token,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7)  # Adjust expiration as needed
        })
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error login user: {str(e)}")

@router.get("/users/me")
def read_current_user(current_user: str = Depends(get_current_user)):
    try:
        user = users_collection.find_one({"email": current_user})
        if user:
            return {
                "username": user["username"],
                "email": user["email"],
                "created_at": user["created_at"],
                "updated_at": user["updated_at"],
            }
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")

@router.post("/refresh-token",status_code=status.HTTP_201_CREATED)
def refresh_token(refresh_token: str):
    try:
        stored_token = refresh_tokens_collection.find_one({"token": refresh_token})

        if not stored_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        if stored_token["expires_at"] < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

        email = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])["sub"]
        new_access_token = create_access_token(data={"sub": email})

        return {"access_token": new_access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating refresh token: {str(e)}")

@router.post("/users/logout")
def logout(refresh_token: str):
    try:
        # Remove the refresh token from the database
        result = refresh_tokens_collection.delete_one({"token": refresh_token})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token"
            )
        
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while logout: {str(e)}")

@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: str):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return {
                    "username": user["username"],
                    "email": user["email"],
                    "created_at": user["created_at"],
                    "updated_at": user["updated_at"],
                }
        raise HTTPException(status_code=404, detail="User not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")
# @router.get("/users-list", response_model=List[User], status_code=status.HTTP_200_OK)
# async def get_all_users():
#     users = []
#     try:
#         for user in users_collection.find({}):  # Use async for non-blocking I/O
#             user["id"] = str(user["_id"])  # Convert ObjectId to string
#             del user["_id"]  # Remove _id to fit the UserInDB model
#             users.append(User(**user))  # Use the Pydantic model for response
#         if not users:
#             raise HTTPException(status_code=404, detail="No users found.")
#         return users
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")

@router.put("/users/{user_id}", status_code=status.HTTP_202_ACCEPTED)
def update_user(user_id: str, updated_data: UserUpdateModel):
    try:
        # Filter out empty fields to avoid unnecessary updates
        update_fields = {k: v for k, v in updated_data.model_dump().items() if v is not None}
        
        # Ensure only allowed fields are updated
        if not update_fields:
            raise HTTPException(status_code=400, detail="No valid fields provided for update.")
        
        if "password" in update_fields:
            update_fields["password"] = get_password_hash(update_fields["password"])

        # Add the `updated_at` field with the current timestamp
        update_fields["updated_at"] = datetime.now(timezone.utc)

        # Perform the update in MongoDB
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_fields}
        )

        if result.modified_count:
            return {"message": "User updated successfully."}
        raise HTTPException(status_code=404, detail="User not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")
    

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: str):
    try:
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
        print("result",type(result))
        if result.deleted_count:
            return {"message": "User deleted successfully."}
        raise HTTPException(status_code=404, detail="User not found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")