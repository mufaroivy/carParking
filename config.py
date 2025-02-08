from dotenv import load_dotenv
import os
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class Config:
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        logger.error("Error: 'JWT_SECRET_KEY' must be set in the .env file.")
        raise ValueError("Error: 'JWT_SECRET_KEY' must be set in the .env file.")

    # Database Configuration
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        logger.error("Error: 'DATABASE_URL' must be set in the .env file.")
        raise ValueError("Error: 'DATABASE_URL' must be set in the .env file.")

    # Application Settings
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't', 'yes']
    HOST: str = os.getenv('HOST', '0.0.0.0')  # Default to listening on all interfaces
    PORT: int = int(os.getenv('PORT', 5000))  # Default port for Flask

    # Optional Configurations
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False  # Disable SQLAlchemy modification tracking
    CORS_ALLOWED_ORIGINS: List[str] = os.getenv('CORS_ALLOWED_ORIGINS', '*').split(',')  # Parse CORS allowed origins

    # Log configuration loading
    logger.info("Configuration loaded successfully.")
    logger.debug(f"JWT_SECRET_KEY: {JWT_SECRET_KEY}")
    logger.debug(f"DATABASE_URL: {DATABASE_URL}")
    logger.debug(f"DEBUG: {DEBUG}")
    logger.debug(f"HOST: {HOST}")
    logger.debug(f"PORT: {PORT}")
    logger.debug(f"CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}")