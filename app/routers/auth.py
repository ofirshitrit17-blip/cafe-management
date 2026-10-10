from fastapi import APIRouter, Request, Form, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.utils.security import generate_otp, create_session_token
from app.services.whatsapp import whatsapp_service
from app.config import get_settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()

# In-memory OTP store for simplicity (use Redis in production)
_otp_store: dict[str, str] = {}


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("employee/login.html", {"request": request})


@router.post("/login/request-otp")
async def request_otp(
    request: Request,
    phone: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    phone = phone.strip().replace("-", "").replace(" ", "")
    if phone.startswith("0"):
        phone = "972" + phone[1:]
    if not phone.startswith("972"):
        phone = "972" + phone

    result = await db.execute(select(User).where(User.phone == phone, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="מספר טלפון לא רשום במערכת")

    otp = generate_otp()
    _otp_store[phone] = otp
    await whatsapp_service.send_otp(phone, otp)

    return templates.TemplateResponse(
        "employee/otp.html",
        {"request": request, "phone": phone},
    )


@router.post("/login/verify-otp")
async def verify_otp(
    request: Request,
    phone: str = Form(...),
    otp: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    stored = _otp_store.get(phone)
    if not stored or stored != otp.strip():
        raise HTTPException(status_code=400, detail="קוד שגוי או שפג תוקף")

    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="משתמש לא נמצא")

    del _otp_store[phone]
    token = create_session_token(user.id, user.phone)
    resp = RedirectResponse(url="/", status_code=303)
    resp.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=settings.SESSION_EXPIRE_DAYS * 86400,
        samesite="lax",
    )
    return resp


@router.post("/logout")
async def logout():
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie(settings.COOKIE_NAME)
    return resp
