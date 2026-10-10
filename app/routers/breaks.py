from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.break_session import BreakSession, BreakStatus
from app.services.break_service import start_break, end_break
from app.utils.time_utils import format_israel, utc_now

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def breaks_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BreakSession).where(
            and_(BreakSession.user_id == user.id, BreakSession.status == BreakStatus.ACTIVE)
        )
    )
    active = result.scalar_one_or_none()
    return templates.TemplateResponse(
        "employee/breaks.html",
        {
            "request": request,
            "user": user,
            "active_break": active,
            "format_israel": format_israel,
            "now": utc_now(),
        },
    )


@router.post("/start")
async def do_start_break(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    duration: int = Form(30),
    break_type: str = Form("general"),
):
    try:
        session = await start_break(db, user, duration_minutes=duration, break_type=break_type)
        await db.commit()
        return {"ok": True, "break_id": session.id, "planned_end": str(session.planned_end_at)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/end")
async def do_end_break(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        session = await end_break(db, user)
        await db.commit()
        return {"ok": True, "break_id": session.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
