"""
Run this script to initialize the database and create tables.
Make sure MySQL is running and .env file is configured.
"""

from database.db_manager import DatabaseManager

if __name__ == "__main__":
    print("Setting up Skill Bartering System database...")
    db_manager = DatabaseManager()
    db_manager.initialize_database()
    print("✓ Database setup complete!")
