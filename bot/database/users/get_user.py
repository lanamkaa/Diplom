from typing import Optional, Tuple
from datetime import datetime
from ..connect import get_db_connection

def get_user_by_telegram_id(telegram_id: int) -> Optional[Tuple[int, str, str, datetime, datetime]]:
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
            SELECT user_id, username, first_name, created_at, last_active_at
            FROM users 
            WHERE telegram_id = %s
            """,
            (telegram_id,)
        )
        
        result = cur.fetchone()
        
        if result:
            return result  #  возвращаем сразу все 5 полей
        return None
        
    except Exception as e:
        print(f"Ошибка при получении пользователя по telegram_id: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
