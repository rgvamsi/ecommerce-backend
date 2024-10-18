from jose import JWTError, jwt
import os
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends,Query
from app.models import users_collection, User, UserLogin, refresh_tokens_collection,UserUpdateModel,PasswordReset, PasswordResetRequest
from app.auth import get_password_hash,create_access_token, verify_password, get_current_user,create_refresh_token
from datetime import datetime, timedelta, timezone
from app.utils.helper import user_helper
from app.services.email_service import send_reset_email

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
def login(user_login: UserLogin):
    print("user_login",user_login)
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
        role = db_user.get("role", "user")
        access_token = create_access_token(data={"sub": user_login.email,"role": role})
        refresh_token = create_refresh_token(data={"sub": user_login.email,"role": role})

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

@router.get("/users", status_code=status.HTTP_200_OK)
def get_all_users(current_user: dict = Depends(get_current_user)):
    try:
        if current_user["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Admins only."
            )

        users = []
        for user in users_collection.find({}):
            users.append(user_helper(user))
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting users list: {str(e)}")

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
    
@router.post("/users/request-password-reset", status_code=status.HTTP_200_OK)
def request_password_reset(request: PasswordResetRequest):
    try:
        user = users_collection.find_one({"email": request.email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Create a reset token (valid for 15 minutes)
        reset_token = jwt.encode(
            {"sub": str(user["_id"]), "exp": datetime.utcnow() + timedelta(minutes=15)},
            SECRET_KEY,
            algorithm="HS256",
        )

        # Send the reset email
        send_reset_email(request.email, reset_token)
        return {"message": "Password reset link sent to your email."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error request for reset password: {str(e)}")
    
@router.post("/users/reset-password/{token}", status_code=status.HTTP_200_OK)
def reset_password(
    token: str, 
    request: PasswordReset
):
    try:
        try:
            # Decode the JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("sub")

            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token.")

        except JWTError:
            raise HTTPException(status_code=401, detail="Token has expired or is invalid.")

        # Fetch user from database
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Verify old password
        if not verify_password(request.old_password, user["password"]):
            raise HTTPException(status_code=401, detail="Incorrect old password.")

        # Hash new password and update the database
        new_hashed_password = get_password_hash(request.new_password)
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": new_hashed_password}},
        )

        return {"message": "Password has been reset successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reset password: {str(e)}")