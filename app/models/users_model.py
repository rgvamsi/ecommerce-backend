from pymongo import MongoClient
from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional
from datetime import datetime


class User(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=20, 
        description="Username must be between 3 and 20 characters."
    )
    email: EmailStr = Field(..., description="Valid email address required.")
    password: str = Field(
        ..., min_length=6, 
        description="Password must be at least 6 characters long."
    )
    firstname:str = Field(
        ..., min_length=3, max_length=20, 
        description="firstname must be between 3 and 50 characters."
    )
    lastname:str = Field(
        ..., min_length=3, max_length=20, 
        description="lastname must be between 3 and 50 characters."
    )
    role: Optional[str] = Field(default="user", description="User role, default is 'user'.")

    # phonenumber:str
    @model_validator(mode='before')
    def check_alphanumeric(cls, values):
        for field in ["username", "firstname", "lastname"]:
            value = values.get(field)
            if value and not value.isalnum():
                raise ValueError(f"{field.capitalize()} must contain only alphanumeric characters.")
        return values

class UserInDB(User):
    id: str
    created_at: datetime
    updated_at: datetime
    
class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Valid email required.")
    password: str = Field(..., description="Password is required.")

class RefreshToken(BaseModel):
    user_id: str = Field(..., description="User ID associated with this token.")
    token: str = Field(..., description="Refresh token string.")
    expires_at: datetime = Field(..., description="Token expiration date.")

class UserUpdateModel(BaseModel):
    firstname:Optional[str] = Field(
        None, min_length=3, max_length=20,
        description="Firstname must be between 3 and 20 characters."
    )
    lastname:Optional[str] = Field(
        None, min_length=3, max_length=20,
        description="Lastname must be between 3 and 20 characters."
    )


class PasswordReset(BaseModel):
    old_password: str = Field(
        ..., min_length=6,
        description="Password must be at least 6 characters long."
    )
    new_password: str = Field(
        ..., min_length=6,
        description="Password must be at least 6 characters long."
    )
