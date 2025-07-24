import asyncio
import random
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from playwright.async_api import async_playwright

class Yad2Scraper:
    def __init__(self):
        self.browser = None
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
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-gpu'
            ]
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='he-IL',
            extra_http_headers={
                'Accept-Language': 'he-IL,he;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
        )
        
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = {
                runtime: {},
            };
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
            # First visit homepage to establish session
            print(f"Visiting Yad2 homepage first...")
            await page.goto('https://www.yad2.co.il', wait_until='domcontentloaded', timeout=60000)
            await self.random_delay(2, 4)
            
            # Now visit the search URL
            url = f"{self.base_url}{neighborhood_id}"
            print(f"Scraping neighborhood {neighborhood_id}: {self.neighborhoods.get(neighborhood_id, 'Unknown')}")
            
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await self.random_delay(3, 6)
            
            # Try multiple selectors for listings
            selectors = [
                '[data-testid="feed-item"]',
                '.feed_item',
                '[class*="feeditem"]',
                '[class*="feed-item"]',
                'div[class*="item_container"]',
                'article[class*="item"]',
                'div[class*="listing"]'
            ]
            
            listings = []
            for selector in selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    listings = await page.query_selector_all(selector)
                    if listings:
                        print(f"Found {len(listings)} listings with selector: {selector}")
                        break
                except:
                    continue
            
            if not listings:
                print(f"No listings found for neighborhood {neighborhood_id}")
                # Save page for debugging
                content = await page.content()
                with open(f'debug_page_{neighborhood_id}.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                return apartments
            
            # Scroll to load more listings
            for _ in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await self.random_delay(1, 2)
            
            # Re-get listings after scrolling
            listings = await page.query_selector_all(selector)
            print(f"Total listings after scrolling: {len(listings)}")
            
            for idx, listing in enumerate(listings):
                try:
                    print(f"Processing listing {idx + 1}/{len(listings)}")
                    apartment = await self.extract_apartment_data(listing, neighborhood_id)
                    if apartment and self.is_recent_listing(apartment.get('publish_date')):
                        apartments.append(apartment)
                        print(f"Added apartment: {apartment.get('title', 'No title')}")
                except Exception as e:
                    print(f"Error extracting apartment data: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping neighborhood {neighborhood_id}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await page.close()
            
        return apartments

    async def extract_apartment_data(self, listing, neighborhood_id: str) -> Dict[str, Any]:
        try:
            # Try multiple ways to find the link
            link_element = await listing.query_selector('a[href*="/item/"]')
            if not link_element:
                link_element = await listing.query_selector('a')
            
            if not link_element:
                print("No link found in listing")
                return None
                
            href = await link_element.get_attribute('href')
            if not href:
                return None
                
            # Make sure href is absolute
            if not href.startswith('http'):
                href = f"https://www.yad2.co.il{href}"
                
            yad2_id_match = re.search(r'/item/([^/?]+)', href)
            if not yad2_id_match:
                print(f"Could not extract ID from href: {href}")
                return None
                
            yad2_id = yad2_id_match.group(1)
            
            # Extract title - try multiple selectors
            title = None
            title_selectors = ['h3', 'h4', '[class*="title"]', '[class*="address"]']
            for sel in title_selectors:
                title_element = await listing.query_selector(sel)
                if title_element:
                    title = await title_element.inner_text()
                    title = title.strip()
                    break
            
            if not title:
                title = "דירה בתל אביב"
            
            # Extract price - try multiple selectors
            price = None
            price_selectors = ['[class*="price"]', '[data-testid="price"]', 'span:has-text("₪")']
            for sel in price_selectors:
                price_element = await listing.query_selector(sel)
                if price_element:
                    price_text = await price_element.inner_text()
                    price_match = re.search(r'[\d,]+', price_text.replace(',', ''))
                    if price_match:
                        price = int(price_match.group())
                        break
            
            if not price:
                price = 0
            
            # Extract rooms
            rooms = None
            room_selectors = ['[class*="room"]', 'span:has-text("חדרים")', '[title*="חדרים"]']
            for sel in room_selectors:
                room_element = await listing.query_selector(sel)
                if room_element:
                    room_text = await room_element.inner_text()
                    room_match = re.search(r'(\d+(?:\.\d+)?)', room_text)
                    if room_match:
                        rooms = float(room_match.group(1))
                        break
            
            if not rooms:
                rooms = 3.5  # Default
            
            # Extract publish date - assume recent for now
            publish_date = datetime.now()
            
            # Extract images
            images = []
            img_elements = await listing.query_selector_all('img')
            for img in img_elements[:5]:  # Limit to 5 images
                src = await img.get_attribute('src')
                if src and not 'placeholder' in src.lower():
                    images.append(src)
            
            apartment = {
                'yad2_id': yad2_id,
                'title': title,
                'price': price,
                'rooms': rooms,
                'floor': None,
                'square_meters': None,
                'address': title,  # Use title as address for now
                'neighborhood': self.neighborhoods.get(neighborhood_id, 'Unknown'),
                'publish_date': publish_date,
                'link': href,
                'images': images
            }
            
            return apartment
            
        except Exception as e:
            print(f"Error in extract_apartment_data: {e}")
            import traceback
            traceback.print_exc()
            return None

    def is_recent_listing(self, publish_date) -> bool:
        if not publish_date:
            return True  # Include if we can't determine date
        
        if isinstance(publish_date, str):
            try:
                publish_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
            except:
                return True
                
        three_days_ago = datetime.now() - timedelta(days=3)
        return publish_date >= three_days_ago

    async def scrape_all(self) -> List[Dict[str, Any]]:
        try:
            await self.setup_browser()
            all_apartments = []
            
            for neighborhood_id in self.neighborhoods.keys():
                apartments = await self.scrape_neighborhood(neighborhood_id)
                all_apartments.extend(apartments)
                print(f"Found {len(apartments)} apartments in {self.neighborhoods[neighborhood_id]}")
                await self.random_delay(5, 10)  # Longer delay between neighborhoods
                
            return all_apartments
            
        finally:
            await self.close_browser()

async def main():
    scraper = Yad2Scraper()
    apartments = await scraper.scrape_all()
    print(f"\nTotal apartments found: {len(apartments)}")
    for apt in apartments:
        print(f"- {apt['title']} - ₪{apt['price']:,} - {apt['rooms']} rooms")

if __name__ == "__main__":
    asyncio.run(main())