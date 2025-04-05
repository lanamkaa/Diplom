from ..connect import get_db_connection

def create_user_if_not_exists(telegram_id: int, username: str, conn=None) -> bool:
    """
    Create a new user only if a user with the same telegram_id doesn't exist.
    Args:
        telegram_id: Telegram user ID
        username: Telegram username
        conn: Optional database connection
    Returns:
        bool: True if user was created or already exists, False if error
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cur = conn.cursor()
    
    try:
        # First check if user exists
        cur.execute("""
        SELECT user_id FROM users WHERE telegram_id = %s
        """, (telegram_id,))
        
        if cur.fetchone() is None:
            # User doesn't exist, create new user
            cur.execute("""
            INSERT INTO users (telegram_id, username)
            VALUES (%s, %s)
            """, (telegram_id, username))
            print(f"Created new user with telegram_id {telegram_id}")
        else:
            print(f"User with telegram_id {telegram_id} already exists")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error checking/creating user: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        if should_close:
            conn.close()