from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timedelta
from typing import List, Optional, Annotated
import asyncio
import hashlib
import secrets

from . import models, schemas, database
from .scraper import run_scraper

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Tel Aviv Apartment Finder", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to track scraping status
is_scraping = False

# Store valid auth tokens (in production, use Redis or database)
valid_tokens = set()


async def verify_token(authorization: Annotated[str | None, Header()] = None):
    """Verify the authentication token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    if token not in valid_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return token

@app.get("/api/apartments", response_model=List[schemas.Apartment])
async def get_apartments(
    skip: int = 0,
    limit: int = 100,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_rooms: Optional[float] = None,
    max_rooms: Optional[float] = None,
    neighborhood_id: Optional[str] = None,
    db: Session = Depends(database.get_db),
    token: str = Depends(verify_token)
):
    query = db.query(models.Apartment).filter(models.Apartment.is_active == True)
    
    # Filter by publish date (last 3 days)
    three_days_ago = datetime.now() - timedelta(days=3)
    query = query.filter(models.Apartment.publish_date >= three_days_ago)
    
    # Apply filters
    if min_price:
        query = query.filter(models.Apartment.price >= min_price)
    if max_price:
        query = query.filter(models.Apartment.price <= max_price)
    if min_rooms:
        query = query.filter(models.Apartment.rooms >= min_rooms)
    if max_rooms:
        query = query.filter(models.Apartment.rooms <= max_rooms)
    if neighborhood_id:
        query = query.filter(models.Apartment.neighborhood_id == neighborhood_id)
    
    # Order by publish date (newest first)
    query = query.order_by(desc(models.Apartment.publish_date))
    
    apartments = query.offset(skip).limit(limit).all()
    return apartments

@app.get("/api/apartments/{apartment_id}", response_model=schemas.Apartment)
async def get_apartment(
    apartment_id: int, 
    db: Session = Depends(database.get_db),
    token: str = Depends(verify_token)
):
    apartment = db.query(models.Apartment).filter(models.Apartment.id == apartment_id).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apartment

async def background_scrape(db: Session):
    global is_scraping
    is_scraping = True
    try:
        await run_scraper(db)
    finally:
        is_scraping = False

@app.post("/api/scrape", response_model=schemas.ScrapeResponse)
async def trigger_scrape(
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    token: str = Depends(verify_token)
):
    global is_scraping
    if is_scraping:
        return schemas.ScrapeResponse(
            success=False,
            message="Scraping is already in progress",
            apartments_found=0,
            new_apartments=0
        )
    
    # Run scraper in background
    background_tasks.add_task(background_scrape, db)
    
    return schemas.ScrapeResponse(
        success=True,
        message="Scraping started in background",
        apartments_found=0,
        new_apartments=0
    )

@app.get("/api/scrape/status")
async def get_scrape_status(token: str = Depends(verify_token)):
    global is_scraping
    return {"is_scraping": is_scraping}

@app.get("/api/stats", response_model=schemas.StatsResponse)
async def get_stats(
    db: Session = Depends(database.get_db),
    token: str = Depends(verify_token)
):
    total = db.query(models.Apartment).count()
    active = db.query(models.Apartment).filter(models.Apartment.is_active == True).count()
    
    three_days_ago = datetime.now() - timedelta(days=3)
    recent = db.query(models.Apartment).filter(
        and_(
            models.Apartment.publish_date >= three_days_ago,
            models.Apartment.is_active == True
        )
    ).count()
    
    last_apartment = db.query(models.Apartment).order_by(desc(models.Apartment.created_at)).first()
    last_scrape = last_apartment.created_at if last_apartment else None
    
    return schemas.StatsResponse(
        total_apartments=total,
        active_apartments=active,
        apartments_last_3_days=recent,
        last_scrape=last_scrape
    )

@app.get("/api/neighborhoods")
async def get_neighborhoods(token: str = Depends(verify_token)):
    neighborhoods = {
        "1483": "נווה צדק",
        "204": "פלורנטין", 
        "1518": "לב העיר",
        "1461": "כרם התימנים",
        "1519": "הצפון הישן",
        "1462": "שבזי"
    }
    return [{"id": k, "name": v} for k, v in neighborhoods.items()]


@app.post("/api/login", response_model=schemas.LoginResponse)
async def login(user_data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    """
    Authenticate user with email and password
    """
    # Hash the provided credentials
    email_hash = hashlib.sha256(user_data.email.encode()).hexdigest()
    password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()
    
    # Find user in database
    user = db.query(models.User).filter(
        models.User.email_hash == email_hash,
        models.User.password_hash == password_hash,
        models.User.is_active == True
    ).first()
    
    if not user:
        return schemas.LoginResponse(
            success=False,
            message="Invalid email or password"
        )
    
    # Update last login
    user.last_login = datetime.now()
    db.commit()
    
    # Generate auth token
    auth_token = secrets.token_hex(32)
    
    # Store token in valid tokens set
    valid_tokens.add(auth_token)
    
    return schemas.LoginResponse(
        success=True,
        message="Login successful",
        auth_token=auth_token
    )

# Mount static files for frontend
import os
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)