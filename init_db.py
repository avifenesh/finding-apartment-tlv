#!/usr/bin/env python3
"""Initialize SQLite database for Yad2 apartment listings."""

import sqlite3
from datetime import datetime

def init_database():
    """Create database tables for storing apartment listings."""
    conn = sqlite3.connect('yad2_listings.db')
    cursor = conn.cursor()
    
    # Create listings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id TEXT PRIMARY KEY,
            price INTEGER,
            rooms REAL,
            address TEXT,
            neighborhood TEXT,
            description TEXT,
            publication_date DATETIME,
            listing_url TEXT,
            scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create images table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listing_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id TEXT,
            image_url TEXT,
            image_order INTEGER,
            FOREIGN KEY (listing_id) REFERENCES listings(id)
        )
    ''')
    
    # Create scrape_history table for tracking scrape runs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scrape_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            listings_found INTEGER DEFAULT 0,
            new_listings INTEGER DEFAULT 0,
            errors TEXT
        )
    ''')
    
    # Create indexes for better query performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_publication_date ON listings(publication_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scraped_at ON listings(scraped_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_listing_images ON listing_images(listing_id)')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()