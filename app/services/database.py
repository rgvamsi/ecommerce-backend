from pymongo import MongoClient

# MongoDB connection string
mongo_client = MongoClient("mongodb+srv://vamshikrishnakatkam:otQOlmIPnpwY4YaT@cluster0.0clej.mongodb.net/")

# Database and collections
db = mongo_client["ecommerce"]
users_collection = db["users"]
refresh_tokens_collection = db["refresh_tokens"]
products_collection = db["products"]
cart_collection=db["cart"]