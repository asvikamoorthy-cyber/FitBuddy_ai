import os
import random
from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .database import get_db_connection

router = APIRouter()

# 🎯 Dynamically locates the templates directory inside app/templates
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(CURRENT_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# 1. Front page router link
@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# 2. Main workflow registration generator endpoint
@router.post("/generate-plan", response_class=HTMLResponse)
async def generate_plan(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    weight: float = Form(...),
    height: float = Form(...),
    days: int = Form(...),
    goal: str = Form(...),
    level: str = Form(...)
):
    generated_schedule = f"=== FITBUDDY WORKOUT BLUEPRINT FOR {name.upper()} ===\n"
    generated_schedule += f"Target Parameters: {days} Days per week split focusing on {goal}.\n\n"
    generated_schedule += "Day 1: Upper Body Power Split Routine\n - Bench Press (3 sets x 10 reps)\n - Dumbbell Rows (3 sets x 12 reps)\n\n"
    generated_schedule += "Day 2: Lower Body Foundational Split Routine\n - Squats (3 sets x 12 reps)\n - Romanian Deadlifts (3 sets x 10 reps)\n\n"
    
    if days >= 3:
        generated_schedule += "Day 3: Core Isolation & HIIT Conditioning\n - Plank Hold Sequences (3 sets x 60 seconds)\n\n"
    if days >= 4:
        generated_schedule += "Day 4: Posterior Chain Variable Focus\n - Incline Dumbbell Press (3 sets x 10 reps)\n\n"
    if days >= 5:
        generated_schedule += "Day 5: Agility Capacities & Core Blast\n - Kettlebell Swings (4 sets x 12 reps)\n"

    # Save cleanly into the database records
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, age, gender, weight, height, days, goal, level, original_plan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, age, gender, weight, height, days, goal, level, generated_schedule))
    conn.commit()
    new_id = cursor.lastrowid
    
    # Force convert database Row structure into standard python dictionary
    row = cursor.execute("SELECT * FROM users WHERE id = ?", (new_id,)).fetchone()
    user_dict = dict(row)
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html", 
        context={
            "user": user_dict,
            "alert_msg": "Profile configuration registered and logged successfully into database log!"
        }
    )

# 3. Dynamic layout dashboard fetch tool URL endpoint
@router.get("/user/{user_id}", response_class=HTMLResponse)
async def view_user_dashboard(request: Request, user_id: int):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Profile registry ID not found.")
        
    return templates.TemplateResponse(
        request=request, 
        name="dashboard.html", 
        context={"user": dict(row)}
    )

# 4. Interactive Feedback handler pipeline route configuration
@router.post("/submit-feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    user_id: int = Form(...),
    feedback_text: str = Form(...)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="User verification key failed.")
    
    user_data = dict(row)
    base_plan = user_data["original_plan"]
    adapted_plan = f"=== ADAPTED PROFILE BLUEPRINT (REVISED VIA USER FEEDBACK) ===\nFeedback: \"{feedback_text}\"\n\n" + base_plan

    cursor.execute("UPDATE users SET updated_plan = ?, feedback_text = ? WHERE id = ?", (adapted_plan, feedback_text, user_id))
    conn.commit()
    
    updated_row = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": dict(updated_row),
            "alert_msg": "Your plan has been updated based on your feedback!"
        }
    )

# 5. Global View All Users administrative tracking route endpoint
@router.get("/users", response_class=HTMLResponse)
async def view_all_users(request: Request):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    conn.close()
    
    # Pack rows cleanly into list of dictionary nodes to feed Jinja2 natively
    all_users = [dict(r) for r in rows]
    return templates.TemplateResponse(
        request=request, 
        name="admin.html", 
        context={"users": all_users}
    )
