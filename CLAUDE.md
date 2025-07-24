# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Yad2 real estate scraper application designed to find 3-4 room apartments for rent in Tel Aviv neighborhoods under 10,000 ILS. The application focuses on showing only recent listings (past 3 days) with images, property details, and direct links.

### Target URLs
The application scrapes the following Yad2 neighborhood searches:
- Neighborhood 1483
- Neighborhood 204  
- Neighborhood 1518
- Neighborhood 1461
- Neighborhood 1519
- Neighborhood 1462

All URLs follow the pattern: `https://www.yad2.co.il/realestate/rent?maxPrice=10000&minRooms=3&maxRooms=4&zoom=15&topArea=2&area=1&city=5000&neighborhood={ID}`

## Architecture Requirements

### Database
- SQLite for persistence of scraped listings
- Store listing details, images, scrape timestamps
- Track which listings have been seen to identify new ones

### Backend/Scraping
- Python-based scraping solution
- Handle CORS and anti-scraping measures from Yad2
- Consider using tools like Selenium, Playwright, or Puppeteer for dynamic content
- Implement rate limiting and respectful scraping practices
- Parse and extract:
  - Listing ID
  - Price
  - Number of rooms
  - Address/neighborhood
  - Images
  - Description
  - Publication date
  - Direct link to listing

### Frontend
- Simple, convenient UI to display listings
- Filter to show only listings from past 3 days
- Display images, key details, and links
- Consider responsive design for mobile viewing

## Development Commands

### Quick Start
```bash
# Run the entire application (recommended)
./run.sh
```

### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Running the Application
```bash
# Start the FastAPI server (from project root)
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the run script
./run.sh
```

### Development Tasks
```bash
# Run scraper manually (from Python shell)
python
>>> from backend.scraper import run_scraper
>>> from backend.database import SessionLocal
>>> import asyncio
>>> db = SessionLocal()
>>> asyncio.run(run_scraper(db))

# Access API documentation
# Navigate to http://localhost:8000/docs
```

## Key Technical Considerations

1. **Yad2 Anti-Scraping**: Yad2 implements various anti-scraping measures including:
   - Dynamic content loading
   - CORS restrictions
   - Rate limiting
   - User-agent detection
   
2. **Data Freshness**: Implement logic to:
   - Track listing publication dates
   - Filter listings older than 3 days
   - Avoid duplicate entries in database

3. **Image Handling**: 
   - Store image URLs or download locally
   - Handle lazy-loaded images
   - Implement fallbacks for missing images

4. **Error Handling**:
   - Network failures
   - Changed HTML structure
   - Rate limit responses
   - Invalid/expired listings