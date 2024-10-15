import jwt
import os
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import users_collection, User, UserLogin, refresh_tokens_collection,RefreshToken
from app.auth import get_password_hash,create_access_token, verify_password, verify_token, get_current_user,create_refresh_token
from bson import ObjectId
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter()

@router.post("/signup")
async def signup(user: User):
    # Check if the email already exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    hashed_password = get_password_hash(user.password)

    # Create new user object with timestamps
    new_user = user.dict()
    new_user["password"] = hashed_password
    new_user["created_at"] = datetime.utcnow()  # Set creation timestamp
    new_user["updated_at"] = datetime.utcnow()  # Set update timestamp
    result = users_collection.insert_one(new_user)

    return {"id": str(result.inserted_id), "message": "User registered successfully"}

@router.post("/login")
async def login(user_login: UserLogin):  # Use the new UserLogin model
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
        "expires_at": datetime.utcnow() + timedelta(days=7)  # Adjust expiration as needed
    })
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/me")
async def read_current_user(current_user: str = Depends(get_current_user)):
    user = users_collection.find_one({"email": current_user})
    if user:
        return {
            "username": user["username"],
            "email": user["email"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@router.post("/refresh-token")
async def refresh_token(refresh_token: str):
    stored_token = refresh_tokens_collection.find_one({"token": refresh_token})

    if not stored_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if stored_token["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    email = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])["sub"]
    new_access_token = create_access_token(data={"sub": email})

    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(refresh_token: str):
    # Remove the refresh token from the database
    result = refresh_tokens_collection.delete_one({"token": refresh_token})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )
    
    return {"message": "Logged out successfully"}