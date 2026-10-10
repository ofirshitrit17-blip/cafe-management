from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def placeholder():
    return {"module": "admin", "status": "coming soon"}
