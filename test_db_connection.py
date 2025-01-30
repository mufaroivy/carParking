import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# Get the DSN from environment variables
dsn = os.getenv("DATABASE_URL")

print(f"Attempting to connect to: {dsn}")

# Test the connection
try:
    connection = psycopg2.connect(dsn)
    print("Successfully connected to the database!")
    connection.close()
except Exception as e:
    print(f"Error connecting to the database: {e}")
