from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal, Dict, Any
from database import transport_collection  # ✅ Now this will work

router = APIRouter()

# Transport request model
class TransportChoice(BaseModel):
    email: str
    trip_id: str
    mode: Literal["bus", "flight", "train"]

# Sample transport details (could be made dynamic later)
transport_data = {
    "bus": {"bus_number": "KA-05-1234", "departure": "10:00 AM", "arrival": "5:00 PM"},
    "flight": {"flight_number": "AI-202", "departure": "6:00 AM", "arrival": "9:00 AM"},
    "train": {"train_number": "12627", "departure": "8:00 PM", "arrival": "6:00 AM"},
}

@router.post("/select-transport", tags=["Transport"])
def select_transport(data: TransportChoice):
    if data.mode not in transport_data:
        raise HTTPException(status_code=400, detail="Invalid transport mode selected")

    transport_details = transport_data[data.mode]

    # Save transport choice
    transport_collection.insert_one(data.dict())

    return {
        "message": f"Transport mode '{data.mode}' selected for {data.email}",
        "details": transport_details,
    }

