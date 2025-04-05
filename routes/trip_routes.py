from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
def test_trip():
    return {"message": "Trip routes are working!"}
