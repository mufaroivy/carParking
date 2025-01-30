import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import os

class Database:
    """
    A class to manage the PostgreSQL connection pool using psycopg2.
    """
    _pool = None  # Class-level attribute for the connection pool

    @classmethod
    def initialize(cls, dsn, minconn=1, maxconn=10):
        """
        Initialize the connection pool with given DSN (Database Source Name).

        Args:
            dsn (str): The connection string for the PostgreSQL database.
            minconn (int): Minimum number of connections in the pool.
            maxconn (int): Maximum number of connections in the pool.
        """
        try:
            # Attempt to create the connection pool using the provided DSN
            cls._pool = psycopg2.pool.SimpleConnectionPool(minconn, maxconn, dsn)
            if cls._pool:
                print("Database connection pool created successfully.")
        except psycopg2.ProgrammingError as e:
            print(f"Programming error during pool initialization: {e}")
            raise
        except psycopg2.Error as e:
            print(f"Error initializing database connection pool: {e}")
            raise

    @classmethod
    def get_connection(cls):
        """
        Get a connection from the pool.

        Returns:
            connection: A connection object from the pool.
        """
        if not cls._pool:
            raise Exception("Error: Database connection pool is not initialized.")
        try:
            connection = cls._pool.getconn()
            if connection:
                return connection
        except psycopg2.Error as e:
            print(f"Error getting connection from pool: {e}")
            raise

    @classmethod
    def return_connection(cls, connection):
        """
        Return a connection to the pool.

        Args:
            connection: The connection object to be returned.
        """
        if cls._pool and connection:
            try:
                cls._pool.putconn(connection)
            except psycopg2.Error as e:
                print(f"Error returning connection to pool: {e}")
                raise

    @classmethod
    def close_all_connections(cls):
        """
        Close all connections in the connection pool.
        """
        if cls._pool:
            try:
                cls._pool.closeall()
                print("All database connections closed.")
            except psycopg2.Error as e:
                print(f"Error closing all connections: {e}")
                raise


# Load environment variables from the .env file
load_dotenv()

# Get the DSN from environment variables
dsn = os.getenv("DATABASE_URL")

if not dsn:
    raise ValueError("Error: 'DATABASE_URL' must be set in the .env file.")

# Debugging: Print the DSN to verify it's being loaded correctly
print(f"Database DSN: {dsn}")

# Attempt to initialize the connection pool
try:
    Database.initialize(dsn)
except Exception as e:
    print(f"Failed to initialize the database: {e}")
    raise
