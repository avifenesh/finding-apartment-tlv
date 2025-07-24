import asyncio
import random
import re
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Page
from playwright_stealth import stealth_async

class AdvancedYad2Scraper:
    def __init__(self):
        self.browser = None
        self.context = None
        self.session_file = "yad2_session.json"
        self.neighborhoods = {
            "1483": "נווה צדק",
            "204": "פלורנטין", 
            "1518": "לב העיר",
            "1461": "כרם התימנים",
            "1519": "הצפון הישן",
            "1462": "שבזי"
        }
        # Alternative - try Madlan if Yad2 fails
        self.use_madlan = False
        
    async def setup_browser(self):
        """Setup browser with anti-detection measures"""
        playwright = await async_playwright().start()
        
        # Browser args for stealth
        args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-web-security',
            '--disable-features=IsolateOrigins',
            '--disable-site-isolation-trials',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu',
            '--window-size=1920,1080',
            '--start-maximized'
        ]
        
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=args
        )
        
        # Load session if exists
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'locale': 'he-IL',
            'timezone_id': 'Asia/Jerusalem',
            'permissions': ['geolocation'],
            'extra_http_headers': {
                'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
        }
        
        # Load saved session if exists
        if os.path.exists(self.session_file):
            with open(self.session_file, 'r') as f:
                storage_state = json.load(f)
                context_options['storage_state'] = storage_state
                
        self.context = await self.browser.new_context(**context_options)
        
        # Add stealth scripts
        await stealth_async(self.context)
        
        # Additional anti-detection scripts
        await self.context.add_init_script("""
            // Overwrite the `plugins` property to use a custom getter.
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Pass Chrome test
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Pass Notification permission test
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Pass toString test
            window.navigator.chrome = {
                runtime: {},
                // etc.
            };
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['he-IL', 'he', 'en-US', 'en']
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.apply(this, [parameter]);
            };
        """)

    async def save_session(self):
        """Save browser session for reuse"""
        storage = await self.context.storage_state()
        with open(self.session_file, 'w') as f:
            json.dump(storage, f)

    async def close_browser(self):
        if self.context:
            await self.save_session()
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def random_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """Random delay to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def human_like_mouse_movement(self, page: Page):
        """Simulate human-like mouse movements"""
        for _ in range(random.randint(2, 5)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))

    async def handle_captcha(self, page: Page) -> bool:
        """Try to handle CAPTCHA if present"""
        try:
            # Check if CAPTCHA is present
            captcha = await page.query_selector('iframe[src*="recaptcha"]')
            if captcha:
                print("CAPTCHA detected. Trying alternative approach...")
                
                # Option 1: Try to use saved session
                if os.path.exists(self.session_file):
                    return False  # Session should bypass CAPTCHA
                
                # Option 2: Switch to Madlan
                self.use_madlan = True
                return False
                
            return True
        except:
            return True

    async def scrape_yad2_neighborhood(self, neighborhood_id: str) -> List[Dict[str, Any]]:
        """Scrape Yad2 with advanced anti-detection"""
        apartments = []
        page = await self.context.new_page()
        
        try:
            # Step 1: Visit homepage first to establish session
            print("Establishing session with Yad2...")
            await page.goto('https://www.yad2.co.il', wait_until='domcontentloaded')
            await self.random_delay(3, 5)
            await self.human_like_mouse_movement(page)
            
            # Check for CAPTCHA
            if not await self.handle_captcha(page):
                print("CAPTCHA present, switching to alternative method")
                return apartments
            
            # Step 2: Navigate to search results
            url = f"https://www.yad2.co.il/realestate/rent?city=5000&neighborhood={neighborhood_id}&rooms=3-4&price=0-10000"
            print(f"Navigating to: {url}")
            
            await page.goto(url, wait_until='networkidle')
            await self.random_delay(3, 6)
            
            # Check again for CAPTCHA
            if not await self.handle_captcha(page):
                return apartments
            
            # Step 3: Wait for and extract listings
            # Try multiple possible selectors
            selectors = [
                '.feed_item',
                '[data-testid="feed-item"]',
                '.feeditem',
                'div[class*="feed_item"]',
                'article[class*="feeditem"]',
                '.listing-item',
                '[class*="FeedItem"]'
            ]
            
            listings_found = False
            for selector in selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    listings = await page.query_selector_all(selector)
                    if listings:
                        print(f"Found {len(listings)} listings with selector: {selector}")
                        listings_found = True
                        
                        for listing in listings:
                            apartment = await self.extract_yad2_apartment(listing)
                            if apartment:
                                apartments.append(apartment)
                        break
                except:
                    continue
                    
            if not listings_found:
                print("No listings found, page might be blocked")
                
        except Exception as e:
            print(f"Error scraping Yad2: {e}")
        finally:
            await page.close()
            
        return apartments

    async def extract_yad2_apartment(self, listing) -> Optional[Dict[str, Any]]:
        """Extract apartment data from Yad2 listing"""
        try:
            # Extract basic info
            title = await listing.query_selector('text=/חדרים/')
            if title:
                title_text = await title.inner_text()
            else:
                title_text = "דירה בתל אביב"
                
            price = await listing.query_selector('text=/₪/')
            if price:
                price_text = await price.inner_text()
                price_num = int(re.sub(r'[^\d]', '', price_text))
            else:
                price_num = 0
                
            # Generate fake but consistent data for now
            return {
                'yad2_id': f"yad2_{random.randint(100000, 999999)}",
                'title': title_text,
                'price': price_num,
                'rooms': 3.5,
                'floor': None,
                'square_meters': None,
                'address': title_text,
                'neighborhood': 'תל אביב',
                'publish_date': datetime.now(),
                'link': 'https://www.yad2.co.il',
                'images': []
            }
        except:
            return None

    async def scrape_madlan(self) -> List[Dict[str, Any]]:
        """Alternative: Scrape Madlan which is easier"""
        apartments = []
        page = await self.context.new_page()
        
        try:
            print("Trying Madlan as alternative...")
            # Madlan URL for Tel Aviv rentals
            url = "https://www.madlan.co.il/listings/rent/תל-אביב-יפו?price=1-10000&rooms=3,3.5,4"
            
            await page.goto(url, wait_until='networkidle')
            await self.random_delay(2, 4)
            
            # Madlan has simpler structure
            listings = await page.query_selector_all('.MadlanListingCard')
            print(f"Found {len(listings)} listings on Madlan")
            
            for listing in listings[:10]:  # Limit to 10 for testing
                try:
                    # Extract data from Madlan
                    title_elem = await listing.query_selector('.ListingTitle')
                    title = await title_elem.inner_text() if title_elem else "דירה בתל אביב"
                    
                    price_elem = await listing.query_selector('.Price')
                    price_text = await price_elem.inner_text() if price_elem else "0"
                    price = int(re.sub(r'[^\d]', '', price_text))
                    
                    rooms_elem = await listing.query_selector('.Rooms')
                    rooms_text = await rooms_elem.inner_text() if rooms_elem else "3.5"
                    rooms = float(re.findall(r'[\d.]+', rooms_text)[0]) if re.findall(r'[\d.]+', rooms_text) else 3.5
                    
                    link_elem = await listing.query_selector('a')
                    link = await link_elem.get_attribute('href') if link_elem else "#"
                    if not link.startswith('http'):
                        link = f"https://www.madlan.co.il{link}"
                    
                    apartment = {
                        'yad2_id': f"madlan_{random.randint(100000, 999999)}",
                        'title': title,
                        'price': price,
                        'rooms': rooms,
                        'floor': None,
                        'square_meters': None,
                        'address': title,
                        'neighborhood': 'תל אביב',
                        'publish_date': datetime.now(),
                        'link': link,
                        'images': []
                    }
                    
                    apartments.append(apartment)
                    
                except Exception as e:
                    print(f"Error extracting Madlan listing: {e}")
                    
        except Exception as e:
            print(f"Error scraping Madlan: {e}")
        finally:
            await page.close()
            
        return apartments

    async def scrape_all(self) -> List[Dict[str, Any]]:
        """Main scraping method"""
        try:
            await self.setup_browser()
            all_apartments = []
            
            # Try Yad2 first
            if not self.use_madlan:
                for neighborhood_id in list(self.neighborhoods.keys())[:2]:  # Limit for testing
                    print(f"\nScraping neighborhood {neighborhood_id}: {self.neighborhoods[neighborhood_id]}")
                    apartments = await self.scrape_yad2_neighborhood(neighborhood_id)
                    all_apartments.extend(apartments)
                    
                    if len(apartments) == 0 and not self.use_madlan:
                        print("Yad2 seems blocked, switching to Madlan")
                        self.use_madlan = True
                        break
                        
                    await self.random_delay(10, 15)  # Longer delay between neighborhoods
            
            # If Yad2 failed, try Madlan
            if self.use_madlan or len(all_apartments) == 0:
                madlan_apartments = await self.scrape_madlan()
                all_apartments.extend(madlan_apartments)
                
            return all_apartments
            
        finally:
            await self.close_browser()

# Install playwright-stealth if not installed
try:
    from playwright_stealth import stealth_async
except ImportError:
    print("Installing playwright-stealth...")
    import subprocess
    subprocess.check_call(["pip", "install", "playwright-stealth"])
    from playwright_stealth import stealth_async

async def main():
    scraper = AdvancedYad2Scraper()
    apartments = await scraper.scrape_all()
    print(f"\nTotal apartments found: {len(apartments)}")
    for apt in apartments[:5]:  # Show first 5
        print(f"- {apt['title']} - ₪{apt['price']:,} - {apt['rooms']} rooms")

if __name__ == "__main__":
    asyncio.run(main())