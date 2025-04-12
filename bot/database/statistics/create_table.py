from ..connect import get_db_connection

def create_link_statistics_table(conn=None):
    """
    Create link_statistics table if it doesn't exist.
    Args:
        conn: Optional database connection. If not provided, creates a new connection.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cur = conn.cursor()
    
    try:
        # Create link_statistics table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS link_statistics (
            stat_id SERIAL PRIMARY KEY,
            url TEXT NOT NULL,
            processing_time FLOAT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("Link statistics table created successfully")
        
    except Exception as e:
        print(f"Error while creating link statistics table: {e}")
        conn.rollback()
    finally:
        cur.close()
        if should_close:
            conn.close()

