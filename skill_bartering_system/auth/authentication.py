# auth/authentication.py
import hashlib
from database.db_manager import DatabaseManager
from utils.validators import validate_email

class AuthenticationManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, email, password, full_name):
        """Register a new user"""
        if not validate_email(email):
            return False, "Invalid email format. Only @geu.ac.in and @gehu.ac.in allowed"
        
        hashed_pw = self.hash_password(password)
        
        try:
            query = '''
                INSERT INTO users (email, password, full_name)
                VALUES (%s, %s, %s)
            '''
            self.db_manager.execute_query(query, (email, hashed_pw, full_name))
            return True, "Registration successful"
        except Exception as e:
            if "Duplicate entry" in str(e):
                return False, "Email already registered"
            return False, f"Error: {str(e)}"
    
    def login(self, email, password):
        """Direct login with email and password"""
        if not validate_email(email):
            return False, None, "Invalid email format"
        
        hashed_pw = self.hash_password(password)
        
        try:
            query = '''
                SELECT id, email, full_name, rating FROM users
                WHERE email = %s AND password = %s
            '''
            user = self.db_manager.fetch_one(query, (email, hashed_pw))
            
            if user:
                return True, user, "Login successful"
            else:
                return False, None, "Invalid credentials"
        except Exception as e:
            return False, None, f"Error: {str(e)}"
    
    def get_user_by_id(self, user_id):
        """Retrieve user information"""
        query = 'SELECT * FROM users WHERE id = %s'
        return self.db_manager.fetch_one(query, (user_id,))
    
    def get_user_by_email(self, email):
        """Retrieve user by email"""
        query = 'SELECT id, email, full_name, rating FROM users WHERE email = %s'
        return self.db_manager.fetch_one(query, (email,))

    def delete_user(self, user_id):
        """Delete user account and all related data (cascading delete)"""
        try:
            query = 'DELETE FROM users WHERE id = %s'
            self.db_manager.execute_query(query, (user_id,))
            return True, "Account deleted successfully"
        except Exception as e:
            return False, f"Error deleting account: {str(e)}"
