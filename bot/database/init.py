from .connect import get_db_connection
from .users.create_table import create_user_table
import sys

def initialize_database():
    """
    Initialize database connection and create users table if it doesn't exist.
    Returns True if successful, False otherwise.
    """
    conn = get_db_connection()
    if not conn:
        print("Failed to establish database connection", file=sys.stderr)
        return False
    
    try:
        create_user_table(conn)
        print("Database initialization successful")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()
