from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from passlib.context import CryptContext
import jwt
import datetime
from typing import List

router = APIRouter()

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017")
db = client["trip_management"]
users_collection = db["users"]
leaders_collection = db["leaders"]

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Pydantic Models
class LoginRequest(BaseModel):
    username: str
    password: str

class UserRegistration(BaseModel):
    full_name: str
    family_name: str
    father_name: str
    mother_name: str
    phone_number: str
    email: EmailStr
    address: str
    gothra: str
    age: int
    gender: str
    blood_group: str
    occupation: str
    password: str

class Leader(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    area: str
    group_id: str
    role: str  # Example: 'Area Leader', 'Mundali Leader'

# 🔹 LOGIN ROUTE (FIRST in order)
@router.post("/auth/login")
def login(user: LoginRequest):
    db_user = users_collection.find_one({"full_name": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    payload = {
        "sub": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"message": "Login successful!", "token": token}

# 🔹 REGISTRATION ROUTE (SECOND in order)
@router.post("/auth/register")
def register_user(user: UserRegistration):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password
    users_collection.insert_one(user_data)
    
    return {"message": "User registered successfully!"}

# 🔹 LEADER REGISTRATION ROUTE (THIRD in order)
@router.post("/auth/leader-register-bulk")
def register_leaders(leaders: List[Leader]):
    inserted_ids = []
    
    for leader in leaders:
        if leaders_collection.find_one({"email": leader.email}):
            raise HTTPException(status_code=400, detail=f"Leader with email {leader.email} already exists")
        
        leader_data = leader.dict()
        result = leaders_collection.insert_one(leader_data)
        inserted_ids.append(str(result.inserted_id))
    
    return {"message": "Leaders registered successfully!", "leader_ids": inserted_ids}
