from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from schemas import TripSchema
from database import trips_collection, users_collection,applications_collection  # ✅ Import users collection
from bson import ObjectId
from typing import Optional, List  # ✅ Add this import


router = APIRouter(prefix="/trip", tags=["Trip Management"])

# ✅ Define Response Model for Swagger UI
class ItineraryItem(BaseModel):
    day: str
    activity: str
    stops: Optional[List[str]] = []  # ✅ Make stops optional

class Schedule(BaseModel):
    start_date: str
    end_date: str

class Transportation(BaseModel):
    mode: str
    details: str

class TripResponse(BaseModel):
    id: str  # _id converted to string
    name: str
    description: str
    location: str
    itinerary: list[ItineraryItem]
    schedule: Schedule
    transportation: Transportation

class IndividualApplicationSchema(BaseModel):
    trip_id: str
    user_id: str


# ✅ Create a trip
@router.post("/create_trip")
async def create_trip(trip: TripSchema):
    new_trip = trip.dict(exclude={"id"})  # ✅ Exclude `id` before inserting
    result = trips_collection.insert_one(new_trip)
    return {"message": "Trip created successfully", "trip_id": str(result.inserted_id)}

# ✅ Get all trips (Fixed for Swagger UI)
@router.get("/trips/", response_model=list[TripResponse])  # ✅ Correct response model
async def get_trips():
    try:
        trips = list(trips_collection.find({}))  # Fetch all trips from MongoDB

        if not trips:
            return []  # ✅ Return empty list if no trips exist

        # ✅ Convert MongoDB _id to string and rename it to "id"
        formatted_trips = []
        for trip in trips:
            trip_data = TripResponse(
                id=str(trip["_id"]),  # Convert ObjectId to string
                name=trip["name"],
                description=trip["description"],
                location=trip["location"],
                itinerary=trip["itinerary"],
                schedule=trip["schedule"],
                transportation=trip["transportation"]
            )
            formatted_trips.append(trip_data)

        return formatted_trips  # ✅ Return the updated trip list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # ✅ Return detailed error

# ✅ Get trip by ID
@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: str):
    trip = trips_collection.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    return TripResponse(
        id=str(trip["_id"]),
        name=trip["name"],
        description=trip["description"],
        location=trip["location"],
        itinerary=trip["itinerary"],
        schedule=trip["schedule"],
        transportation=trip["transportation"]
    )

# ✅ Delete trip by ID
@router.delete("/{trip_id}", response_model=dict)
async def delete_trip(trip_id: str):
    result = trips_collection.delete_one({"_id": ObjectId(trip_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Trip not found")

    return {"message": "Trip deleted successfully"}


# ✅ ADD "ADMIN CAN ADD USER" FEATURE BELOW THIS LINE ✅

# ✅ Define User Schema
class UserSchema(BaseModel):
    name: str
    email: str

# ✅ Admin can add users
@router.post("/admin/add-user", response_model=dict)
async def add_user(user: UserSchema):
    # Check if the user already exists
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = {"name": user.name, "email": user.email}
    result = users_collection.insert_one(new_user)
    return {"message": "User added successfully", "user_id": str(result.inserted_id)}


@router.post("/apply-individual", response_model=dict)
async def apply_individual(application: IndividualApplicationSchema):
    user = users_collection.find_one({"_id": ObjectId(application.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    trip = trips_collection.find_one({"_id": ObjectId(application.trip_id)})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    application_data = {
        "trip_id": application.trip_id,
        "user_id": application.user_id,
        "status": "Pending"
    }
    result = applications_collection.insert_one(application_data)
    return {"message": "Individual application submitted", "application_id": str(result.inserted_id)}

