from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timedelta
from typing import List, Optional
import asyncio

from . import models, schemas, database, scraper

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Yad2 Apartment Scraper", version="1.0.0")

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "https://*.cloudfront.net",  # Allow CloudFront domains
        "https://*.execute-api.amazonaws.com",  # Allow API Gateway
        # Add your specific CloudFront domain here after deployment
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Global variable to track scraping status
is_scraping = False

@app.get("/api/apartments", response_model=List[schemas.Apartment])
async def get_apartments(
    skip: int = 0,
    limit: int = 100,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_rooms: Optional[float] = None,
    max_rooms: Optional[float] = None,
    neighborhood_id: Optional[str] = None,
    db: Session = Depends(database.get_db)
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
async def get_apartment(apartment_id: int, db: Session = Depends(database.get_db)):
    apartment = db.query(models.Apartment).filter(models.Apartment.id == apartment_id).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apartment

async def background_scrape(db: Session):
    global is_scraping
    is_scraping = True
    try:
        await scraper.run_scraper(db)
    finally:
        is_scraping = False

@app.post("/api/scrape", response_model=schemas.ScrapeResponse)
async def trigger_scrape(
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db)
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
async def get_scrape_status():
    global is_scraping
    return {"is_scraping": is_scraping}

@app.get("/api/stats", response_model=schemas.StatsResponse)
async def get_stats(db: Session = Depends(database.get_db)):
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
async def get_neighborhoods():
    neighborhoods = {
        "1483": "נווה צדק",
        "204": "פלורנטין", 
        "1518": "לב העיר",
        "1461": "כרם התימנים",
        "1519": "הצפון הישן",
        "1462": "שבזי"
    }
    return [{"id": k, "name": v} for k, v in neighborhoods.items()]

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)