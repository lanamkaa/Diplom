from typing import Optional, Tuple
from ..connect import get_db_connection

def get_user_by_telegram_id(telegram_id: int) -> Optional[Tuple[int, str]]:
    """
    Get user information by their Telegram ID.
    
    Args:
        telegram_id (int): Telegram user ID
        
    Returns:
        Optional[Tuple[int, str]]: Tuple of (user_id, username) if user exists, None otherwise
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get user information
        cur.execute(
            """
            SELECT user_id, username 
            FROM users 
            WHERE telegram_id = %s
            """,
            (telegram_id,)
        )
        
        result = cur.fetchone()
        
        if result:
            return result[0], result[1]  # user_id, username
        return None
        
    except Exception as e:
        print(f"Error getting user by telegram_id: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
