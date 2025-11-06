# config/config.py
import os
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

# For Streamlit Cloud deployment, use st.secrets
def get_secret(key, default=None):
    """Get secret from environment variables or Streamlit secrets"""
    # First try environment variables (for local development)
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value
    
    # Fall back to Streamlit secrets (for cloud deployment)
    try:
        import streamlit as st
        return st.secrets[key]
    except:
        return default

MYSQL_HOST = get_secret('MYSQL_HOST', 'localhost')
MYSQL_USER = get_secret('MYSQL_USER', 'root')
MYSQL_PASSWORD = get_secret('MYSQL_PASSWORD', 'Rattu@1021')
MYSQL_DATABASE = get_secret('MYSQL_DATABASE', 'skill_barter_db')
MYSQL_PORT = int(get_secret('MYSQL_PORT', 3306))

DATABASE_CONFIG = {
    'host': MYSQL_HOST,
    'user': MYSQL_USER,
    'password': MYSQL_PASSWORD,
    'database': MYSQL_DATABASE,
    'port': MYSQL_PORT
}

ALLOWED_DOMAINS = ['geu.ac.in', 'gehu.ac.in']
SECRET_KEY = get_secret('SECRET_KEY', 'skill-barter-secret-key')
SESSION_TIMEOUT = 3600  # 1 hour

# Email Configuration
EMAIL_HOST = get_secret('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(get_secret('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = get_secret('EMAIL_HOST_USER', 'rajchandan02468@gmail.com')  # Your Gmail address
EMAIL_HOST_PASSWORD = get_secret('EMAIL_HOST_PASSWORD', '8210877658@abc')  # Your app password

EMAIL_CONFIG = {
    'host': EMAIL_HOST,
    'port': EMAIL_PORT,
    'use_tls': EMAIL_USE_TLS,
    'username': EMAIL_HOST_USER,
    'password': EMAIL_HOST_PASSWORD
}
