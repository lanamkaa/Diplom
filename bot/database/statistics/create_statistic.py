from typing import Optional
from ..connect import get_db_connection

def create_link_statistic(url: str, processing_time: float) -> Optional[int]:
    """
    Create a new link check statistic entry in the database.
    
    Args:
        url (str): The URL that was checked
        processing_time (float): The time taken to process the URL in seconds
        
    Returns:
        Optional[int]: The ID of the created statistic entry
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insert the statistic and return the stat_id
        cur.execute(
            """
            INSERT INTO link_statistics (url, processing_time)
            VALUES (%s, %s)
            RETURNING stat_id
            """,
            (url, processing_time)
        )
        
        stat_id = cur.fetchone()[0]
        conn.commit()
        return stat_id
        
    except Exception as e:
        print(f"Error creating link statistic: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
