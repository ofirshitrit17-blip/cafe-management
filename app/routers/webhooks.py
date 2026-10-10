from fastapi import APIRouter, Request, Response
from app.config import get_settings
router = APIRouter()
settings = get_settings()

@router.get("/whatsapp")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(status_code=403)

@router.post("/whatsapp")
async def receive_webhook(request: Request):
    body = await request.json()
    # Handle incoming messages / status updates later
    return {"status": "ok"}
