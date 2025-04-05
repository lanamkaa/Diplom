from ..connect import get_db_connection

def create_text_responses_table(conn=None):
    """
    Create text_responses table if it doesn't exist.
    Args:
        conn: Optional database connection. If not provided, creates a new connection.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cur = conn.cursor()
    
    try:
        # Create text_responses table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS text_responses (
            text_response_id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
            response_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("Text responses table created successfully")
        
    except Exception as e:
        print(f"Error while creating text responses table: {e}")
        conn.rollback()
    finally:
        cur.close()
        if should_close:
            conn.close()
