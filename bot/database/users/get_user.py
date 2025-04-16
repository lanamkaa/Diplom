from typing import Optional, Tuple
from ..connect import get_db_connection

def get_user_by_telegram_id(telegram_id: int) -> Optional[Tuple[int, str]]:
    """
    Получение информации о пользователе по их Telegram ID.
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

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
        print(f"Ошибка при получении пользователя по telegram_id: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
