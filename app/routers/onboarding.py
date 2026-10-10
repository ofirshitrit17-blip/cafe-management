from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def placeholder():
    return {"module": "onboarding", "status": "coming soon"}
