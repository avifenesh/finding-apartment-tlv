from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

class Apartment(Base):
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True, index=True)
    yad2_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    rooms = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    neighborhood = Column(String, nullable=False)
    neighborhood_id = Column(String, nullable=False)
    description = Column(Text)
    images = Column(JSON, default=list)
    link = Column(String, nullable=False)
    publish_date = Column(DateTime, nullable=False)
    floor = Column(String)
    square_meters = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    last_seen = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)