from pydantic import BaseModel
from typing import List, Dict, Optional

class ItineraryItem(BaseModel):
    day: str
    activity: str
    stops: Optional[List[str]] = []  # ✅ New field for stops (optional)

class Schedule(BaseModel):
    start_date: str
    end_date: str

class Transportation(BaseModel):
    mode: str
    details: str

class TripSchema(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    location: str
    itinerary: List[ItineraryItem]  # ✅ Now includes stops
    schedule: Schedule
    transportation: Transportation
