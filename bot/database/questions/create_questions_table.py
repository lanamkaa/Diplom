from ..connect import get_db_connection

def create_questions_table(conn=None):
    """
    Create questions table if it doesn't exist.
    Args:
        conn: Optional database connection. If not provided, creates a new connection.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cur = conn.cursor()
    
    try:
        # Create questions table without foreign key constraints
        cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            question_id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
            question TEXT NOT NULL,
            answer_text TEXT,
            answer_rating INTEGER CHECK (answer_rating IS NULL OR (answer_rating >= 1 AND answer_rating <= 5)),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("Questions table created successfully")
        
    except Exception as e:
        print(f"Error while creating questions table: {e}")
        conn.rollback()
    finally:
        cur.close()
        if should_close:
            conn.close()
