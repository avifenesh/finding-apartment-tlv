# Finding Apartment TLV

A web application for finding apartments in Tel Aviv neighborhoods.

## Features

- Search for 3-4 room apartments under 10,000 ILS
- Filter by neighborhood, price, and room count
- Shows only recent listings (past 3 days)
- Hebrew RTL interface
- Database-based authentication

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Python
- **Frontend**: HTML, JavaScript, Tailwind CSS
- **Database**: SQLite

## Local Development

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Frontend

Open `frontend/index.html` in a web browser or serve with any static file server.

## Project Structure

```
├── backend/
│   ├── main.py          # FastAPI application
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # Database configuration
│   └── scraper*.py      # Data aggregation modules
├── frontend/
│   ├── index.html       # Main page
│   ├── login.html       # Login page
│   ├── script.js        # Frontend logic
│   └── style.css        # Styles
└── requirements.txt     # Python dependencies
```

## License

MIT