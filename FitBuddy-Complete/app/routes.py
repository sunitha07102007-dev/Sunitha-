from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db, save_user, save_plan, get_latest_plan, update_plan, get_all_users
from .schemas import UserInput
from .ai_service import ai, demo_workout, demo_tip

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def context(request, **kwargs):
    return {"request": request, "app_name": settings.app_name, **kwargs}

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context=context(request))

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    user_id: str = Form(...), name: str = Form(...), age: int = Form(...), weight: float = Form(...),
    goal: str = Form(...), intensity: str = Form(...), db: Session = Depends(get_db)
):
    try:
        data = UserInput(user_id=user_id, name=name, age=age, weight=weight, goal=goal, intensity=intensity)
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="index.html", context=context(request, error=f"Please check your inputs: {exc}"), status_code=422)
    workout, demo = ai.safe_call(ai.workout, data)
    if demo: workout = demo_workout(data)
    tip, tip_demo = ai.safe_call(ai.nutrition, data)
    if tip_demo: tip = demo_tip(data)
    user = save_user(db, data)
    plan = save_plan(db, user, workout, tip)
    return templates.TemplateResponse(request=request, name="result.html", context=context(request, user=data, plan=plan, workout_plan=workout, nutrition_tip=tip, demo_mode=demo or tip_demo))

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(request: Request, user_id: str = Form(...), feedback: str = Form(...), db: Session = Depends(get_db)):
    plan = get_latest_plan(db, user_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No plan found for this User ID")
    data = type("Profile", (), {"name": plan.user.name, "age": plan.user.age, "weight": plan.user.weight, "goal": plan.user.goal, "intensity": plan.user.intensity})()
    revised, demo = ai.safe_call(ai.update, data, plan.original_plan, feedback)
    if demo: revised = demo_workout(data) + f"\n\n[Feedback applied in demo mode]\nRequested change: {feedback}"
    tip, tip_demo = ai.safe_call(ai.nutrition, data)
    if tip_demo: tip = demo_tip(data)
    update_plan(db, plan, feedback, revised, tip)
    return templates.TemplateResponse(request=request, name="result.html", context=context(request, user=data, plan=plan, workout_plan=revised, nutrition_tip=tip, updated=True, demo_mode=demo or tip_demo))

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, token: str | None = None, db: Session = Depends(get_db)):
    if token != settings.admin_token:
        return templates.TemplateResponse(request=request, name="admin_login.html", context=context(request, error="Enter the configured admin token to continue."), status_code=401)
    users = get_all_users(db)
    return templates.TemplateResponse(request=request, name="all_users.html", context=context(request, users=users, token=token))

@router.get("/health")
def health():
    return {"status":"ok", "ai_configured": settings.ai_enabled, "demo_mode": settings.demo_mode or not settings.gemini_api_key}
