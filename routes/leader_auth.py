from fastapi import APIRouter, HTTPException
from database import leaders_collection
from pydantic import BaseModel
from typing import List
from bson import ObjectId

router = APIRouter(prefix="/leader", tags=["Leader Management"])

# Leader Schema
class LeaderSchema(BaseModel):
    full_name: str
    email: str
    phone_number: str
    area: str
    group_id: str
    role: str  # Example: 'Area Leader', 'Mundali Leader'

# Bulk Register Leaders
@router.post("/register-bulk")
async def register_leaders(leaders: List[LeaderSchema]):
    inserted_ids = []
    
    for leader in leaders:
        if leaders_collection.find_one({"email": leader.email}):
            raise HTTPException(status_code=400, detail=f"Leader with email {leader.email} already exists")
        
        leader_data = leader.dict()
        result = leaders_collection.insert_one(leader_data)
        inserted_ids.append(str(result.inserted_id))
    
    return {"message": "Leaders registered successfully!", "leader_ids": inserted_ids}

# Delete a Leader
@router.delete("/delete/{leader_id}")
async def delete_leader(leader_id: str):
    result = leaders_collection.delete_one({"_id": ObjectId(leader_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Leader not found")
    
    return {"message": "Leader deleted successfully"}
