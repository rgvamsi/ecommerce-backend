from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

mongo_client=MongoClient("mongodb+srv://vamshikrishnakatkam:otQOlmIPnpwY4YaT@cluster0.0clej.mongodb.net/")
db=mongo_client["ecommerce"]
users_collection = db["users"]
refresh_tokens_collection = db["refresh_tokens"]


class User(BaseModel):
    username: str
    email: str
    password: str

class UserInDB(User):
    id: str
    created_at: datetime
    updated_at: datetime
    
class UserLogin(BaseModel):
    email: str
    password: str
    
class RefreshToken(BaseModel):
    user_id: str
    token: str
    expires_at: datetime

class UserUpdateModel(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None 
