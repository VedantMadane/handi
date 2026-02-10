import math
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
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
async def ledger(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * page_size

    # Get total count
    count_result = await db.execute(select(func.count()).select_from(Donation))
    total_donations = count_result.scalar() or 0

    # Get paginated results
    result = await db.execute(
        select(Donation)
        .order_by(Donation.id.desc())
        .offset(offset)
        .limit(page_size)
    )
    donations = result.scalars().all()

    # Calculate total pages
    total_pages = math.ceil(total_donations / page_size)

    return render(request, "ledger.html", {
        "donations": donations,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total_donations": total_donations
    })

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
