from ..connect import get_db_connection

def create_user_table():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create users table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("User table created successfully")
        
    except Exception as e:
        print(f"Error while creating user table: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
