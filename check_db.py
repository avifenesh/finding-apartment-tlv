#!/usr/bin/env python3
"""Check database entries"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from backend.models import Apartment
from datetime import datetime, timedelta

def check_database():
    db = SessionLocal()
    try:
        # Total apartments
        total = db.query(Apartment).count()
        print(f"Total apartments in database: {total}")
        
        # Active apartments
        active = db.query(Apartment).filter(Apartment.is_active == True).count()
        print(f"Active apartments: {active}")
        
        # Recent apartments (last 3 days)
        three_days_ago = datetime.now() - timedelta(days=3)
        recent = db.query(Apartment).filter(
            Apartment.publish_date >= three_days_ago,
            Apartment.is_active == True
        ).count()
        print(f"Apartments from last 3 days: {recent}")
        
        # Show some recent apartments
        if total > 0:
            print("\nMost recent apartments:")
            print("-" * 60)
            apartments = db.query(Apartment).order_by(Apartment.publish_date.desc()).limit(5).all()
            for apt in apartments:
                print(f"\n{apt.title}")
                print(f"  Price: ₪{apt.price:,}")
                print(f"  Rooms: {apt.rooms}")
                print(f"  Neighborhood: {apt.neighborhood}")
                print(f"  Published: {apt.publish_date}")
                print(f"  ID: {apt.listing_id}")
        else:
            print("\n❌ No apartments in database yet!")
            print("You need to run the scraper to populate the database.")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_database()