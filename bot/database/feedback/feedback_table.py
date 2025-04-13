from ..connect import get_db_connection

def create_feedback_table(conn=None):
    """
    Create feedback table if it doesn't exist.
    Args:
        conn: Optional database connection. If not provided, creates a new connection.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cur = conn.cursor()
    
    try:
        # Create feedback table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            question_id INTEGER,
            is_dialog_feedback BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("Feedback table created successfully")
        
    except Exception as e:
        print(f"Error while creating feedback table: {e}")
        conn.rollback()
    finally:
        cur.close()
        if should_close:
            conn.close()
