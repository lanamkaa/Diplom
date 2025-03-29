import psycopg2
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

def get_db_connection():
    try:
        # Prefer DATABASE_URL if set, otherwise construct connection string
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            print(f"Using DATABASE_URL: {database_url}")
            conn = psycopg2.connect(database_url)
        else:
            print("Constructing connection parameters manually")
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "db"),
                database=os.getenv("DB_NAME", "diplomdb"),
                user=os.getenv("DB_USER", "postgres"),
                password=str(os.getenv("DB_PASSWORD", "postgres")),
                port=os.getenv("DB_PORT", "5432"),
                client_encoding='utf8'
            )
        
        print("Successfully connected to the database!")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}", file=sys.stderr)
        print(f"Connection details:", file=sys.stderr)
        print(f"Host: {os.getenv('DB_HOST', 'db')}", file=sys.stderr)
        print(f"Database: {os.getenv('DB_NAME', 'diplomdb')}", file=sys.stderr)
        print(f"User: {os.getenv('DB_USER', 'postgres')}", file=sys.stderr)
        print(f"Port: {os.getenv('DB_PORT', '5432')}", file=sys.stderr)
        print(f"Full environment: {dict(os.environ)}", file=sys.stderr)
        return None
