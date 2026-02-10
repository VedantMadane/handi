from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Event, Donation, Attendance
from app.config import STRIPE_PUBLISHABLE_KEY, PAYPAL_CLIENT_ID

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Helper to add 'gettext' aka '_' to the context
def render(request: Request, name: str, context: dict):
    # Retrieve the gettext function from request state (set in middleware)
    _ = getattr(request.state, "gettext", lambda x: x)
    context.update({"request": request, "_": _})
    return templates.TemplateResponse(name, context)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return render(request, "index.html", {
        "stripe_publishable_key": STRIPE_PUBLISHABLE_KEY,
        "paypal_client_id": PAYPAL_CLIENT_ID
    })

@router.get("/ledger", response_class=HTMLResponse)
async def ledger(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Donation).order_by(Donation.id.desc()))
    donations = result.scalars().all()
    return render(request, "ledger.html", {"donations": donations})

@router.get("/events", response_class=HTMLResponse)
async def events_list(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).order_by(Event.start_time))
    events = result.scalars().all()
    return render(request, "events.html", {"events": events})

@router.post("/events/{event_id}/rsvp", response_class=HTMLResponse)
async def rsvp(event_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    # Demo Mode: Assume User ID 1 is doing this.
    # In real app: get_current_user dependency
    user_id = 1

    # Check if already RSVP'd
    result = await db.execute(select(Attendance.id).where(Attendance.event_id == event_id, Attendance.user_id == user_id))
    existing = result.scalar()

    if not existing:
        new_attendance = Attendance(event_id=event_id, user_id=user_id, status="registered")
        db.add(new_attendance)
        await db.commit()
        return "<button class='btn btn-success' disabled>Registered</button>"
    else:
        return "<button class='btn btn-success' disabled>Already Registered</button>"

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return "<h1>Login Page (Placeholder)</h1>"
