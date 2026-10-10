from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.services.attendance_service import clock_in, clock_out, get_today_status
from app.utils.time_utils import format_israel

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


@router.get("/", response_class=HTMLResponse)
async def attendance_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    status = await get_today_status(db, user.id)
    return templates.TemplateResponse(
        "employee/attendance.html",
        {
            "request": request,
            "user": user,
            "status": status,
            "format_israel": format_israel,
        },
    )


@router.post("/clock-in")
async def do_clock_in(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ip = get_client_ip(request)
    try:
        event = await clock_in(db, user, ip)
        await db.commit()
        return {"ok": True, "event_id": event.id, "time": str(event.event_time)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/clock-out")
async def do_clock_out(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ip = get_client_ip(request)
    try:
        event = await clock_out(db, user, ip)
        await db.commit()
        return {"ok": True, "event_id": event.id, "time": str(event.event_time)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
