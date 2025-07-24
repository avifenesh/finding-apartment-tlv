from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List, Optional

class ApartmentBase(BaseModel):
    yad2_id: str
    title: str
    price: int
    rooms: float
    address: str
    neighborhood: str
    neighborhood_id: str
    description: Optional[str] = None
    images: List[str] = []
    link: str
    publish_date: datetime
    floor: Optional[str] = None
    square_meters: Optional[int] = None

class ApartmentCreate(ApartmentBase):
    pass

class ApartmentUpdate(BaseModel):
    is_active: Optional[bool] = None
    last_seen: Optional[datetime] = None

class Apartment(ApartmentBase):
    id: int
    created_at: datetime
    last_seen: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    apartments_found: int
    new_apartments: int

class StatsResponse(BaseModel):
    total_apartments: int
    active_apartments: int
    apartments_last_3_days: int
    last_scrape: Optional[datetime]