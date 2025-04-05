from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Create or connect to the database
db = client["trip_management"]

# Define collections
users_collection = db["users"]
transport_collection = db["transport"]
trips_collection = db["trips"]
room_collection = db["rooms"]  # ✅ Collection for room allotment
