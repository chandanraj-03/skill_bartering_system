
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from config.config import DATABASE_CONFIG

class DatabaseManager:
    def __init__(self):
        self.config = DATABASE_CONFIG
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = mysql.connector.connect(**self.config)
            yield conn
            conn.commit()
        except Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def execute_query(self, query, params=None):
        """Execute a single query"""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            conn.commit()
            cursor.close()
    
    def fetch_one(self, query, params=None):
        """Fetch a single row"""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return result
    
    def fetch_all(self, query, params=None):
        """Fetch all rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
    
    def initialize_database(self):
        """Create database and all necessary tables"""
        # First create the database if it doesn't exist
        config_without_db = self.config.copy()
        db_name = config_without_db.pop('database')
        
        try:
            conn = mysql.connector.connect(**config_without_db)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.close()
            conn.close()
            print(f"✓ Database '{db_name}' created or already exists")
        except Error as e:
            print(f"Error creating database: {e}")
            raise e

        # Now create all tables
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    bio TEXT,
                    profile_image LONGTEXT,
                    rating FLOAT DEFAULT 5.0,
                    total_exchanges INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            ''')
            
            # Skills table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS skills (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    skill_name VARCHAR(255) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    description TEXT,
                    proficiency_level VARCHAR(50),
                    is_offering BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_user_id (user_id),
                    INDEX idx_category (category)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            ''')
            
            # Exchanges table (updated for group support)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exchanges (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    initiator_id INT NOT NULL,
                    recipient_id INT NULL,  -- NULL for group exchanges
                    initiator_skill_id INT NOT NULL,
                    recipient_skill_id INT NULL,  -- NULL for group exchanges
                    status VARCHAR(50) DEFAULT 'pending',
                    is_group BOOLEAN DEFAULT FALSE,
                    title VARCHAR(255),  -- For group exchanges
                    description TEXT,   -- For group exchanges
                    max_participants INT DEFAULT 2,
                    rating_from_initiator INT,
                    rating_from_recipient INT,
                    review_from_initiator TEXT,
                    review_from_recipient TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP NULL,
                    FOREIGN KEY (initiator_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (initiator_skill_id) REFERENCES skills(id) ON DELETE CASCADE,
                    FOREIGN KEY (recipient_skill_id) REFERENCES skills(id) ON DELETE CASCADE,
                    INDEX idx_initiator (initiator_id),
                    INDEX idx_recipient (recipient_id),
                    INDEX idx_status (status),
                    INDEX idx_is_group (is_group)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            ''')

            # Exchange participants table for group exchanges
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exchange_participants (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    exchange_id INT NOT NULL,
                    user_id INT NOT NULL,
                    skill_id INT NOT NULL,
                    role VARCHAR(50) DEFAULT 'participant',  -- 'initiator', 'participant'
                    status VARCHAR(50) DEFAULT 'pending',    -- 'pending', 'accepted', 'rejected'
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (exchange_id) REFERENCES exchanges(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_participant (exchange_id, user_id),
                    INDEX idx_exchange (exchange_id),
                    INDEX idx_user (user_id),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            ''')
            
            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sender_id INT NOT NULL,
                    recipient_id INT NOT NULL,
                    exchange_id INT,
                    message TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (exchange_id) REFERENCES exchanges(id) ON DELETE CASCADE,
                    INDEX idx_sender (sender_id),
                    INDEX idx_recipient (recipient_id),
                    INDEX idx_exchange (exchange_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            ''')
            
            # Ratings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ratings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    exchange_id INT NOT NULL,
                    rater_id INT NOT NULL,
                    rated_user_id INT NOT NULL,
                    rating INT NOT NULL,
                    review TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (exchange_id) REFERENCES exchanges(id) ON DELETE CASCADE,
                    FOREIGN KEY (rater_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (rated_user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_rating (exchange_id, rater_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            ''')
            
            conn.commit()
            print("Database initialized successfully!")