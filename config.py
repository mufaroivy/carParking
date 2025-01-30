from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("Error: 'JWT_SECRET_KEY' must be set in the .env file.")

    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("Error: 'DATABASE_URL' must be set in the .env file.")

    # Application Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't', 'yes']
    HOST = os.getenv('HOST', '0.0.0.0')  # Default to listening on all interfaces
    PORT = int(os.getenv('PORT', 5000))  # Default port for Flask
    
    # Optional Configurations
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable SQLAlchemy modification tracking
    CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '*')  # For handling CORS
