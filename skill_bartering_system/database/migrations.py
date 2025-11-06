# database/migrations.py
"""
Database migration script for adding new features
Run this script once to update the existing database with new fields
"""
import sys
import os

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from config.config import DATABASE_CONFIG

def run_migrations():
    """Run all database migrations"""
    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    print("Running database migrations...")
    
    # Add attachment fields to messages table if they don't exist
    print("Adding attachment fields to messages table...")
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN attachment_data LONGTEXT")
        conn.commit()
        print("✓ Added attachment_data column")
    except mysql.connector.Error as err:
        if err.errno == 1060:  # Duplicate column name
            print("✓ attachment_data column already exists")
        else:
            print(f"✗ Error adding attachment_data: {err}")
    
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN attachment_name VARCHAR(255)")
        conn.commit()
        print("✓ Added attachment_name column")
    except mysql.connector.Error as err:
        if err.errno == 1060:
            print("✓ attachment_name column already exists")
        else:
            print(f"✗ Error adding attachment_name: {err}")
    
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN attachment_type VARCHAR(100)")
        conn.commit()
        print("✓ Added attachment_type column")
    except mysql.connector.Error as err:
        if err.errno == 1060:
            print("✓ attachment_type column already exists")
        else:
            print(f"✗ Error adding attachment_type: {err}")
    
    # Add social media fields to users table if they don't exist
    print("\nAdding social media fields to users table...")
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN linkedin_url VARCHAR(255)")
        conn.commit()
        print("✓ Added linkedin_url column")
    except mysql.connector.Error as err:
        if err.errno == 1060:
            print("✓ linkedin_url column already exists")
        else:
            print(f"✗ Error adding linkedin_url: {err}")
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN github_url VARCHAR(255)")
        conn.commit()
        print("✓ Added github_url column")
    except mysql.connector.Error as err:
        if err.errno == 1060:
            print("✓ github_url column already exists")
        else:
            print(f"✗ Error adding github_url: {err}")
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN twitter_url VARCHAR(255)")
        conn.commit()
        print("✓ Added twitter_url column")
    except mysql.connector.Error as err:
        if err.errno == 1060:
            print("✓ twitter_url column already exists")
        else:
            print(f"✗ Error adding twitter_url: {err}")
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN portfolio_url VARCHAR(255)")
        conn.commit()
        print("✓ Added portfolio_url column")
    except mysql.connector.Error as err:
        if err.errno == 1060:
            print("✓ portfolio_url column already exists")
        else:
            print(f"✗ Error adding portfolio_url: {err}")
    
    cursor.close()
    conn.close()
    print("\n✓ All migrations completed successfully!")

if __name__ == "__main__":
    run_migrations()
