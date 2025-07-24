import asyncio
from playwright.async_api import async_playwright

async def test_yad2():
    print("Starting Yad2 test...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Run with GUI to see what's happening
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='he-IL',
            extra_http_headers={
                'Accept-Language': 'he-IL,he;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        # Add scripts to hide automation
        await context.add_init_script("""
            // Overwrite the `plugins` property to use a custom getter.
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Pass Chrome Test
            window.chrome = {
                runtime: {},
            };
            
            // Pass Permissions Test
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        page = await context.new_page()
        
        try:
            print("Navigating to Yad2...")
            url = "https://www.yad2.co.il/realestate/rent?maxPrice=10000&minRooms=3&maxRooms=4&city=5000"
            
            # First visit the homepage
            await page.goto('https://www.yad2.co.il', wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(3)
            
            # Then navigate to the search results
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(5)
            
            print("Page loaded!")
            
            # Take screenshot
            await page.screenshot(path='yad2-test.png')
            print("Screenshot saved as yad2-test.png")
            
            # Check for listings
            listings = await page.query_selector_all('[data-testid="feed-item"]')
            print(f"Found {len(listings)} listings")
            
            if len(listings) == 0:
                # Check for alternative selectors
                listings = await page.query_selector_all('.feeditem')
                print(f"Found {len(listings)} listings with alternative selector")
                
                # Try another selector
                listings = await page.query_selector_all('[class*="feed_item"]')
                print(f"Found {len(listings)} listings with class selector")
            
            # Get page content
            content = await page.content()
            with open('yad2-content.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Page content saved to yad2-content.html")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_yad2())