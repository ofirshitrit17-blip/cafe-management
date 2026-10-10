from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import get_settings
from app.database import engine, Base, AsyncSessionLocal
from app.routers import auth, attendance, breaks, shifts, tasks, checklists, onboarding, admin, webhooks
from app.services.notifications import process_pending_notifications
from app.services.break_service import check_overdue_breaks

settings = get_settings()
scheduler = AsyncIOScheduler()


async def background_worker():
    async with AsyncSessionLocal() as db:
        try:
            await process_pending_notifications(db)
            await check_overdue_breaks(db)
            await db.commit()
        except Exception as e:
            print(f"Background worker error: {e}")
            await db.rollback()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    scheduler.add_job(background_worker, "interval", seconds=settings.QUEUE_POLL_SECONDS)
    scheduler.start()
    print("Scheduler started")
    yield
    # Shutdown
    scheduler.shutdown()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Routers
app.include_router(auth.router, tags=["auth"])
app.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
app.include_router(breaks.router, prefix="/breaks", tags=["breaks"])
app.include_router(shifts.router, prefix="/shifts", tags=["shifts"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(checklists.router, prefix="/checklists", tags=["checklists"])
app.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("employee/home.html", {"request": request, "title": settings.APP_NAME})


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
