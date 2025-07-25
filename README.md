# Finding Apartment TLV

A web application that scrapes Yad2 real estate listings to find 3-4 room apartments for rent in Tel Aviv neighborhoods under 10,000 ILS. The app displays only listings from the past three days, complete with images, property details, and direct links.

**Login Page:** [frontend/login.html](frontend/login.html)

## Features

- 🏠 Automated scraping of 6 Tel Aviv neighborhoods
- 🕒 Shows only recent listings (past 3 days)
- 🖼️ Displays apartment images in a carousel
- 📊 Real-time statistics and filtering
- 🔍 Filter by neighborhood, price, and room count
- 🤖 Anti-scraping bypass with Playwright
- 💾 SQLite database for persistence
- 🚀 FastAPI backend with modern async Python
- 🎨 Clean, responsive UI in Hebrew

## Neighborhoods Covered

- נווה צדק (Neve Tzedek)
- פלורנטין (Florentin)
- לב העיר (City Center)
- כרם התימנים (Kerem HaTeimanim)
- הצפון הישן (Old North)
- שבזי (Shabazi)

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/finding-apartment-tlv.git
   cd finding-apartment-tlv
   ```

2. **Run the application:**
   ```bash
   ./run.sh
   ```
   This script will:
   - Create a virtual environment
   - Install all dependencies
   - Install Playwright browsers
   - Start the FastAPI server

3. **Open your browser:**
   Navigate to http://localhost:8000

## Manual Setup

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run the server
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Usage

1. **View Apartments:** The main page shows all apartments from the last 3 days
2. **Filter Results:** Use the dropdown filters for neighborhood, price, and rooms
3. **Run Scraper:** Click "הפעל סריקה" to fetch latest listings
4. **View Details:** Click on apartment images or the Yad2 link

## API Endpoints

- `GET /api/apartments` - List apartments with filters
- `GET /api/apartments/{id}` - Get apartment details
- `POST /api/scrape` - Trigger manual scrape
- `GET /api/stats` - Get statistics
- `GET /api/neighborhoods` - List neighborhoods

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy
- **Scraping:** Playwright (headless Chromium)
- **Database:** SQLite
- **Frontend:** Vanilla JS, Tailwind CSS
- **Deployment:** Uvicorn ASGI server

## Development

To modify the scraper settings:
- Edit `backend/scraper.py` for scraping logic
- Update `backend/models.py` for database schema
- Modify `frontend/` files for UI changes

## Notes

- The scraper includes anti-detection measures and random delays
- Respects Yad2's server load with rate limiting
- Database tracks when apartments were last seen
- Auto-refreshes frontend every 30 seconds

## Contributing

Feel free to open issues or submit pull requests for improvements!