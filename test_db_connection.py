import psycopg2
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection(dsn: str) -> bool:
    """
    Test the connection to the PostgreSQL database.

    Args:
        dsn (str): The connection string for the PostgreSQL database.

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    connection = None
    try:
        connection = psycopg2.connect(dsn)
        logger.info("Successfully connected to the database!")
        return True
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        return False
    finally:
        if connection:
            connection.close()
            logger.info("Database connection closed.")

if __name__ == '__main__':
    # Load environment variables from .env
    load_dotenv()

    # Get the DSN from environment variables
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        logger.error("Error: 'DATABASE_URL' must be set in the .env file.")
        exit(1)

    logger.info(f"Attempting to connect to: {dsn}")

    # Test the connection
    if test_database_connection(dsn):
        logger.info("Database connection test completed successfully.")
    else:
        logger.error("Database connection test failed.")