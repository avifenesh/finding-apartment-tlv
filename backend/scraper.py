import asyncio
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Page, Browser
from sqlalchemy.orm import Session
from . import models, schemas
from dateutil.parser import parse as parse_date
import re

class Yad2Scraper:
    def __init__(self):
        self.browser: Browser = None
        self.context = None
        self.neighborhoods = {
            "1483": "נווה צדק",
            "204": "פלורנטין", 
            "1518": "לב העיר",
            "1461": "כרם התימנים",
            "1519": "הצפון הישן",
            "1462": "שבזי"
        }
        self.base_url = "https://www.yad2.co.il/realestate/rent?maxPrice=10000&minRooms=3&maxRooms=4&zoom=15&topArea=2&area=1&city=5000&neighborhood="

    async def setup_browser(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='he-IL',
        )
        
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    async def close_browser(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def random_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def scrape_neighborhood(self, neighborhood_id: str) -> List[Dict[str, Any]]:
        apartments = []
        page = await self.context.new_page()
        
        try:
            url = f"{self.base_url}{neighborhood_id}"
            print(f"Scraping neighborhood {neighborhood_id}: {self.neighborhoods.get(neighborhood_id, 'Unknown')}")
            
            await page.goto(url, wait_until='networkidle', timeout=60000)
            await self.random_delay(2, 5)
            
            # Wait for listings to load
            await page.wait_for_selector('[data-testid="feed-item"]', timeout=30000)
            
            # Scroll to load all listings
            for _ in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await self.random_delay(1, 2)
            
            # Get all listing items
            listings = await page.query_selector_all('[data-testid="feed-item"]')
            
            for listing in listings:
                try:
                    apartment = await self.extract_apartment_data(listing, neighborhood_id)
                    if apartment and self.is_recent_listing(apartment.get('publish_date')):
                        apartments.append(apartment)
                except Exception as e:
                    print(f"Error extracting apartment data: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping neighborhood {neighborhood_id}: {e}")
        finally:
            await page.close()
            
        return apartments

    async def extract_apartment_data(self, listing, neighborhood_id: str) -> Dict[str, Any]:
        try:
            # Extract Yad2 ID from the listing
            link_element = await listing.query_selector('a[href*="/item/"]')
            if not link_element:
                return None
                
            href = await link_element.get_attribute('href')
            yad2_id_match = re.search(r'/item/([^/?]+)', href)
            if not yad2_id_match:
                return None
                
            yad2_id = yad2_id_match.group(1)
            full_link = f"https://www.yad2.co.il{href}" if href.startswith('/') else href
            
            # Extract price
            price_element = await listing.query_selector('[data-testid="price"]')
            price_text = await price_element.inner_text() if price_element else "0"
            price = int(re.sub(r'[^\d]', '', price_text) or 0)
            
            # Extract rooms
            rooms_element = await listing.query_selector('span:has-text("חדרים")')
            rooms_text = await rooms_element.inner_text() if rooms_element else "0"
            rooms_match = re.search(r'(\d+(?:\.\d+)?)', rooms_text)
            rooms = float(rooms_match.group(1)) if rooms_match else 0
            
            # Extract address
            address_element = await listing.query_selector('[data-testid="address"]')
            address = await address_element.inner_text() if address_element else "Unknown"
            
            # Extract title
            title_element = await listing.query_selector('h3')
            title = await title_element.inner_text() if title_element else f"{rooms} חדרים ב{address}"
            
            # Extract publish date
            date_element = await listing.query_selector('span:has-text("לפני")')
            publish_date = datetime.now()
            if date_element:
                date_text = await date_element.inner_text()
                publish_date = self.parse_relative_date(date_text)
            
            # Extract images
            images = []
            img_elements = await listing.query_selector_all('img[src*="images"]')
            for img in img_elements[:5]:  # Limit to 5 images
                src = await img.get_attribute('src')
                if src and 'yad2' in src:
                    images.append(src)
            
            # Extract additional details
            details_elements = await listing.query_selector_all('[data-testid="property-feature"]')
            floor = None
            square_meters = None
            
            for detail in details_elements:
                text = await detail.inner_text()
                if 'קומה' in text:
                    floor = text
                elif 'מ"ר' in text:
                    meters_match = re.search(r'(\d+)', text)
                    if meters_match:
                        square_meters = int(meters_match.group(1))
            
            return {
                'yad2_id': yad2_id,
                'title': title,
                'price': price,
                'rooms': rooms,
                'address': address,
                'neighborhood': self.neighborhoods.get(neighborhood_id, 'Unknown'),
                'neighborhood_id': neighborhood_id,
                'description': '',  # Would need to click into listing for full description
                'images': images,
                'link': full_link,
                'publish_date': publish_date,
                'floor': floor,
                'square_meters': square_meters
            }
            
        except Exception as e:
            print(f"Error extracting apartment data: {e}")
            return None

    def parse_relative_date(self, date_text: str) -> datetime:
        now = datetime.now()
        
        if 'עכשיו' in date_text or 'הרגע' in date_text:
            return now
        elif 'דקה' in date_text or 'דקות' in date_text:
            minutes = re.search(r'(\d+)', date_text)
            if minutes:
                return now - timedelta(minutes=int(minutes.group(1)))
        elif 'שעה' in date_text or 'שעות' in date_text:
            hours = re.search(r'(\d+)', date_text)
            if hours:
                return now - timedelta(hours=int(hours.group(1)))
        elif 'יום' in date_text or 'ימים' in date_text:
            days = re.search(r'(\d+)', date_text)
            if days:
                return now - timedelta(days=int(days.group(1)))
            elif 'אתמול' in date_text:
                return now - timedelta(days=1)
        elif 'שבוע' in date_text:
            return now - timedelta(weeks=1)
            
        return now

    def is_recent_listing(self, publish_date: datetime) -> bool:
        if not publish_date:
            return True
        three_days_ago = datetime.now() - timedelta(days=3)
        return publish_date >= three_days_ago

    async def scrape_all_neighborhoods(self) -> List[Dict[str, Any]]:
        all_apartments = []
        
        try:
            await self.setup_browser()
            
            for neighborhood_id in self.neighborhoods.keys():
                apartments = await self.scrape_neighborhood(neighborhood_id)
                all_apartments.extend(apartments)
                await self.random_delay(3, 6)  # Delay between neighborhoods
                
        finally:
            await self.close_browser()
            
        return all_apartments

async def run_scraper(db: Session) -> schemas.ScrapeResponse:
    scraper = Yad2Scraper()
    
    try:
        apartments_data = await scraper.scrape_all_neighborhoods()
        
        new_count = 0
        total_count = len(apartments_data)
        
        for apt_data in apartments_data:
            # Check if apartment already exists
            existing = db.query(models.Apartment).filter_by(yad2_id=apt_data['yad2_id']).first()
            
            if existing:
                # Update last_seen
                existing.last_seen = datetime.now()
                existing.is_active = True
            else:
                # Create new apartment
                new_apartment = models.Apartment(**apt_data)
                db.add(new_apartment)
                new_count += 1
        
        # Mark apartments not seen in this scrape as inactive
        three_hours_ago = datetime.now() - timedelta(hours=3)
        db.query(models.Apartment).filter(
            models.Apartment.last_seen < three_hours_ago,
            models.Apartment.is_active == True
        ).update({'is_active': False})
        
        db.commit()
        
        return schemas.ScrapeResponse(
            success=True,
            message=f"Successfully scraped {total_count} apartments",
            apartments_found=total_count,
            new_apartments=new_count
        )
        
    except Exception as e:
        db.rollback()
        return schemas.ScrapeResponse(
            success=False,
            message=f"Scraping failed: {str(e)}",
            apartments_found=0,
            new_apartments=0
        )