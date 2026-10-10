import httpx
from typing import Optional
from app.config import get_settings

settings = get_settings()


class WhatsAppService:
    def __init__(self):
        self.base_url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}"
        self.token = settings.WHATSAPP_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID

    async def send_text(self, to_phone: str, body: str) -> dict:
        """Send a simple text message (within 24h window or for testing)."""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone.lstrip("+"),
            "type": "text",
            "text": {"body": body},
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def send_template(
        self,
        to_phone: str,
        template_name: str,
        language_code: str = "he",
        components: Optional[list] = None,
    ) -> dict:
        """Send an approved WhatsApp template message."""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone.lstrip("+"),
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
            },
        }
        if components:
            payload["template"]["components"] = components
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def send_otp(self, to_phone: str, otp_code: str) -> dict:
        """Send OTP. Prefer approved template; fallback to text in dev."""
        if settings.APP_ENV == "development" and not self.token:
            print(f"[DEV] OTP for {to_phone}: {otp_code}")
            return {"messages": [{"id": "dev-otp"}]}
        # In production use a pre-approved authentication template
        try:
            return await self.send_template(
                to_phone,
                template_name="otp_login",
                components=[{
                    "type": "body",
                    "parameters": [{"type": "text", "text": otp_code}],
                }],
            )
        except Exception:
            # Fallback
            return await self.send_text(to_phone, f"קוד הכניסה שלך למערכת בית הקפה: {otp_code}")


whatsapp_service = WhatsAppService()
