#!/usr/bin/env python3
"""Populate database with test data without external dependencies"""

import sqlite3
import random
from datetime import datetime, timedelta

def populate_database():
    # Connect to SQLite database
    conn = sqlite3.connect('apartments.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS apartments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        listing_id TEXT UNIQUE,
        title TEXT NOT NULL,
        price INTEGER NOT NULL,
        rooms REAL NOT NULL,
        address TEXT NOT NULL,
        neighborhood TEXT NOT NULL,
        neighborhood_id TEXT NOT NULL,
        description TEXT,
        images TEXT,
        link TEXT NOT NULL,
        publish_date TIMESTAMP NOT NULL,
        floor TEXT,
        square_meters INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    neighborhoods = {
        "נווה צדק": {"id": "1483", "min_price": 7000, "max_price": 10000},
        "פלורנטין": {"id": "204", "min_price": 5500, "max_price": 8500},
        "לב העיר": {"id": "1518", "min_price": 6000, "max_price": 9500},
        "כרם התימנים": {"id": "1461", "min_price": 6500, "max_price": 9000},
        "הצפון הישן": {"id": "1519", "min_price": 5000, "max_price": 8000},
        "שבזי": {"id": "1462", "min_price": 5500, "max_price": 8000}
    }
    
    streets = {
        "נווה צדק": ["שבזי", "חבצלת", "לילינבלום", "יחיאלי"],
        "פלורנטין": ["פלורנטין", "ויטל", "אברבנאל", "מטלון"],
        "לב העיר": ["אלנבי", "נחלת בנימין", "רוטשילד", "אחד העם"],
        "כרם התימנים": ["עמיעד", "מלצ'ט", "פינס", "נחום"],
        "הצפון הישן": ["דיזנגוף", "בן יהודה", "ארלוזורוב", "ז'בוטינסקי"],
        "שבזי": ["שבזי", "אחד העם", "העלייה", "נחמני"]
    }
    
    apartments_added = 0
    
    for neighborhood, data in neighborhoods.items():
        # Generate 3-5 apartments per neighborhood
        num_apartments = random.randint(3, 5)
        
        for _ in range(num_apartments):
            # Generate apartment data
            rooms_options = [3, 3.5, 4]
            rooms = random.choice(rooms_options)
            
            # Price based on rooms and neighborhood
            base_price = random.randint(data['min_price'], data['max_price'])
            if rooms == 4:
                base_price += random.randint(500, 1500)
            elif rooms == 3:
                base_price -= random.randint(0, 500)
            
            # Square meters based on rooms
            if rooms == 3:
                sqm = random.randint(55, 70)
            elif rooms == 3.5:
                sqm = random.randint(65, 80)
            else:  # 4 rooms
                sqm = random.randint(75, 95)
            
            # Random floor
            max_floor = random.choice([3, 4, 5, 6, 8])
            floor = random.randint(0, max_floor)
            
            # Generate title
            street = random.choice(streets[neighborhood])
            title = f"דירת {rooms} חדרים ברחוב {street}"
            
            # Random publish date within last 3 days
            days_ago = random.randint(0, 2)
            hours_ago = random.randint(0, 23)
            publish_date = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
            # Generate ID
            apt_id = f"gen_{neighborhood[:3]}_{random.randint(100000, 999999)}"
            
            # Address
            address = f"{street} {random.randint(1, 150)}, {neighborhood}"
            
            # Insert apartment
            try:
                cursor.execute('''
                INSERT INTO apartments (
                    listing_id, title, price, rooms, address, neighborhood, 
                    neighborhood_id, link, publish_date, floor, square_meters,
                    created_at, last_seen, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), 1)
                ''', (
                    apt_id, title, base_price, rooms, address, neighborhood,
                    data['id'], f"https://example.com/listing/{apt_id}",
                    publish_date, str(floor), sqm
                ))
                apartments_added += 1
            except sqlite3.IntegrityError:
                # Skip if apartment already exists
                pass
    
    conn.commit()
    
    # Show statistics
    cursor.execute("SELECT COUNT(*) FROM apartments")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM apartments WHERE is_active = 1")
    active = cursor.fetchone()[0]
    
    print(f"✅ Database populated successfully!")
    print(f"   Added {apartments_added} new apartments")
    print(f"   Total apartments in database: {total}")
    print(f"   Active apartments: {active}")
    
    # Show some recent apartments
    cursor.execute("""
        SELECT title, price, rooms, neighborhood, publish_date 
        FROM apartments 
        WHERE is_active = 1 
        ORDER BY publish_date DESC 
        LIMIT 5
    """)
    
    print("\nMost recent apartments:")
    print("-" * 60)
    for row in cursor.fetchall():
        title, price, rooms, neighborhood, publish_date = row
        print(f"{title} - ₪{price:,} - {rooms} rooms - {neighborhood}")
    
    conn.close()

if __name__ == "__main__":
    populate_database()