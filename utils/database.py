import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import os
import logging
from typing import Optional

load_dotenv()

class Database:
    _pool = None

    @classmethod
    def initialize(cls, dsn, minconn=1, maxconn=10):
        try:
            cls._pool = psycopg2.pool.SimpleConnectionPool(minconn, maxconn, dsn)
        except Exception as e:
            logging.error(f"Error initializing database pool: {e}")
            raise

    @classmethod
    def get_connection(cls):
        if not cls._pool:
            raise Exception("Database pool not initialized.")
        return cls._pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        if cls._pool and connection:
            cls._pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        if cls._pool:
            cls._pool.closeall()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

dsn = os.getenv("DATABASE_URL")

if not dsn:
    logger.error("Error: 'DATABASE_URL' must be set in the .env file.")
    raise ValueError("Error: 'DATABASE_URL' must be set in the .env file.")

# Debugging: Log the DSN to verify it's being loaded correctly
logger.debug(f"Database DSN: {dsn}")

# Attempt to initialize the connection pool
try:
    Database.initialize(dsn)
except Exception as e:
    logger.error(f"Failed to initialize the database: {e}")
    raise