import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database=os.getenv("DB_NAME", "telegram_bot"),
            user=os.getenv("DB_USER", "postgres"),
            password=str(os.getenv("DB_PASSWORD")),  # Convert to string explicitly
            port=os.getenv("DB_PORT", "5432"),
            client_encoding='utf8'
        )
        print("Successfully connected to the database!")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None
