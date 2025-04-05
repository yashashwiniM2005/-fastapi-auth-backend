from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from database import room_collection  # Ensure this collection exists in your database.py

router = APIRouter()

# Room allotment request model
class RoomAllotment(BaseModel):
    email: str
    trip_id: str
    destination: str
    building: str
    room_number: str
    allotted_members: List[str]

@router.post("/allot-room", tags=["Room Allotment"])
def allot_room(data: RoomAllotment):
    # Optionally, check if room already allotted to same trip and user
    existing = room_collection.find_one({
        "email": data.email,
        "trip_id": data.trip_id,
        "room_number": data.room_number
    })
    if existing:
        raise HTTPException(status_code=400, detail="Room already allotted to this user for this trip")

    # Save to DB
    room_collection.insert_one(data.dict())

    return {
        "message": f"Room {data.room_number} allotted successfully for {data.email}",
        "room_details": data.dict()
    }
