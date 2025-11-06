from config.config import ALLOWED_DOMAINS
import re

def validate_email(email):
    """Validate email format and domain"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    
    domain = email.split('@')[1]
    return domain in ALLOWED_DOMAINS

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, "Password valid"

def validate_skill_input(skill_name, category, description):
    """Validate skill input"""
    if not skill_name or len(skill_name) < 2:
        return False, "Skill name must be at least 2 characters"
    if not category or len(category) < 2:
        return False, "Category must be at least 2 characters"
    if not description or len(description) < 10:
        return False, "Description must be at least 10 characters"
    return True, "Valid"
