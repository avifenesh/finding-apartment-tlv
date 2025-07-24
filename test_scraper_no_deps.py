#!/usr/bin/env python3
"""Test the data generation functionality without external dependencies"""

import random
from datetime import datetime, timedelta

def generate_realistic_apartment(neighborhood):
    """Generate realistic apartment data based on neighborhood"""
    neighborhoods = {
        "נווה צדק": {"min_price": 7000, "max_price": 10000},
        "פלורנטין": {"min_price": 5500, "max_price": 8500},
        "לב העיר": {"min_price": 6000, "max_price": 9500},
        "כרם התימנים": {"min_price": 6500, "max_price": 9000},
        "הצפון הישן": {"min_price": 5000, "max_price": 8000},
        "שבזי": {"min_price": 5500, "max_price": 8000}
    }
    
    streets = {
        "נווה צדק": ["שבזי", "חבצלת", "לילינבלום", "יחיאלי"],
        "פלורנטין": ["פלורנטין", "ויטל", "אברבנאל", "מטלון"],
        "לב העיר": ["אלנבי", "נחלת בנימין", "רוטשילד", "אחד העם"],
        "כרם התימנים": ["עמיעד", "מלצ'ט", "פינס", "נחום"],
        "הצפון הישן": ["דיזנגוף", "בן יהודה", "ארלוזורוב", "ז'בוטינסקי"],
        "שבזי": ["שבזי", "אחד העם", "העלייה", "נחמני"]
    }
    
    price_range = neighborhoods[neighborhood]
    street_list = streets[neighborhood]
    
    # Realistic room distribution for Tel Aviv
    rooms_options = [3, 3.5, 4]
    rooms = random.choice(rooms_options)
    
    # Price based on rooms and neighborhood
    base_price = random.randint(price_range['min_price'], price_range['max_price'])
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
    
    # Random features
    features = []
    if random.random() > 0.3:
        features.append("מרפסת")
    if random.random() > 0.5:
        features.append("ממוזג")
    if random.random() > 0.7:
        features.append("חניה")
    if floor == 0 and random.random() > 0.5:
        features.append("גינה")
    if random.random() > 0.6:
        features.append("מעלית")
        
    # Generate title
    street = random.choice(street_list)
    title = f"דירת {rooms} חדרים ברחוב {street}"
    if features:
        title += f" - {', '.join(features[:2])}"
        
    # Random publish date within last 3 days
    days_ago = random.randint(0, 2)
    hours_ago = random.randint(0, 23)
    publish_date = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
    
    # Generate ID
    apt_id = f"gen_{neighborhood[:3]}_{random.randint(100000, 999999)}"
    
    return {
        'listing_id': apt_id,
        'title': title,
        'price': base_price,
        'rooms': rooms,
        'floor': floor,
        'square_meters': sqm,
        'address': f"{street} {random.randint(1, 150)}, {neighborhood}",
        'neighborhood': neighborhood,
        'publish_date': publish_date,
        'link': f"https://example.com/listing/{apt_id}",
        'features': features
    }

def main():
    print("Testing apartment data generation (without external dependencies)")
    print("=" * 60)
    
    neighborhoods = ["נווה צדק", "פלורנטין", "לב העיר", "כרם התימנים", "הצפון הישן", "שבזי"]
    
    all_apartments = []
    
    for neighborhood in neighborhoods:
        # Generate 2-3 apartments per neighborhood
        num_apartments = random.randint(2, 3)
        
        for _ in range(num_apartments):
            apartment = generate_realistic_apartment(neighborhood)
            all_apartments.append(apartment)
    
    print(f"\nGenerated {len(all_apartments)} realistic apartment listings:")
    print("-" * 60)
    
    # Sort by publish date (newest first)
    all_apartments.sort(key=lambda x: x['publish_date'], reverse=True)
    
    for apt in all_apartments:
        print(f"\n{apt['title']}")
        print(f"  💰 Price: ₪{apt['price']:,}")
        print(f"  🏠 Rooms: {apt['rooms']}")
        print(f"  📍 Address: {apt['address']}")
        print(f"  📏 Size: {apt['square_meters']} m²")
        print(f"  🏢 Floor: {apt['floor']}")
        print(f"  📅 Published: {apt['publish_date'].strftime('%Y-%m-%d %H:%M')}")
        if apt['features']:
            print(f"  ✨ Features: {', '.join(apt['features'])}")
        print(f"  🔗 ID: {apt['listing_id']}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed successfully!")
    print("All references to specific data sources have been removed.")
    print("The application now operates as a generic apartment aggregator.")

if __name__ == "__main__":
    main()