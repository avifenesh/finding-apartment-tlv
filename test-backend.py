#!/usr/bin/env python3
"""
Quick test script to verify backend is working
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_backend():
    print("🔍 Testing Yad2 Apartment Finder Backend...\n")
    
    # Test 1: Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is running!")
            print(f"   Health check: {response.json()}")
        else:
            print("❌ Backend is not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 8000")
        print("   Run: ./run.sh")
        return
    
    # Test 2: Get neighborhoods
    print("\n📍 Testing neighborhoods endpoint...")
    response = requests.get(f"{BASE_URL}/api/neighborhoods")
    if response.status_code == 200:
        neighborhoods = response.json()
        print(f"✅ Found {len(neighborhoods)} neighborhoods:")
        for n in neighborhoods:
            print(f"   - {n['name']} (ID: {n['id']})")
    
    # Test 3: Get statistics
    print("\n📊 Testing statistics endpoint...")
    response = requests.get(f"{BASE_URL}/api/stats")
    if response.status_code == 200:
        stats = response.json()
        print("✅ Statistics:")
        print(f"   - Total apartments: {stats['total_apartments']}")
        print(f"   - Active apartments: {stats['active_apartments']}")
        print(f"   - Recent (3 days): {stats['apartments_last_3_days']}")
        if stats['last_scrape']:
            last_scrape = datetime.fromisoformat(stats['last_scrape'].replace('Z', '+00:00'))
            print(f"   - Last scrape: {last_scrape.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 4: Get apartments
    print("\n🏠 Testing apartments endpoint...")
    response = requests.get(f"{BASE_URL}/api/apartments?limit=5")
    if response.status_code == 200:
        apartments = response.json()
        print(f"✅ Found {len(apartments)} apartments")
        if apartments:
            print("   Sample apartment:")
            apt = apartments[0]
            print(f"   - Title: {apt['title']}")
            print(f"   - Price: ₪{apt['price']:,}")
            print(f"   - Rooms: {apt['rooms']}")
            print(f"   - Neighborhood: {apt['neighborhood']}")
    
    # Test 5: Check scraping status
    print("\n🤖 Testing scraper status...")
    response = requests.get(f"{BASE_URL}/api/scrape/status")
    if response.status_code == 200:
        status = response.json()
        print(f"✅ Scraping in progress: {status['is_scraping']}")
    
    print("\n🎉 Backend tests complete!")
    print("\nNext steps:")
    print("1. Make backend accessible with ngrok: ngrok http 8000")
    print("2. Update frontend/script.js with the ngrok URL")
    print("3. Push changes to GitHub")
    print("4. Visit: https://avifenesh.github.io/finding-apartment-tlv/")

if __name__ == "__main__":
    test_backend()