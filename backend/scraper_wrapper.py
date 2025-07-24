from .scraper_simple import SimpleApartmentScraper
from . import models
from sqlalchemy.orm import Session
from datetime import datetime

async def run_scraper(db: Session):
    """Run the scraper and save results to database"""
    print("Starting scraper...")
    
    scraper = SimpleApartmentScraper()
    try:
        apartments = await scraper.scrape_all()
        print(f"Scraper found {len(apartments)} apartments")
        
        new_count = 0
        for apt_data in apartments:
            # Check if apartment already exists
            existing = db.query(models.Apartment).filter_by(listing_id=apt_data['listing_id']).first()
            if existing:
                # Update existing apartment
                for key, value in apt_data.items():
                    if key != 'images':
                        setattr(existing, key, value)
                existing.last_seen = datetime.now()
            else:
                # Create new apartment
                apartment = models.Apartment(
                    listing_id=apt_data['listing_id'],
                    title=apt_data['title'],
                    price=apt_data['price'],
                    rooms=apt_data['rooms'],
                    floor=apt_data.get('floor'),
                    square_meters=apt_data.get('square_meters'),
                    address=apt_data['address'],
                    neighborhood=apt_data['neighborhood'],
                    publish_date=apt_data['publish_date'],
                    link=apt_data['link'],
                    last_seen=datetime.now(),
                    is_active=True
                )
                db.add(apartment)
                
                # Add images
                for img_url in apt_data.get('images', []):
                    image = models.ApartmentImage(
                        apartment_id=apartment.id,
                        url=img_url
                    )
                    db.add(image)
                
                new_count += 1
        
        db.commit()
        print(f"Added {new_count} new apartments to database")
        
        # Mark old apartments as inactive
        three_days_ago = datetime.now() - timedelta(days=3)
        db.query(models.Apartment).filter(
            models.Apartment.last_seen < three_days_ago
        ).update({"is_active": False})
        db.commit()
        
        return len(apartments), new_count
        
    except Exception as e:
        print(f"Error in run_scraper: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0