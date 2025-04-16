from ..connect import get_db_connection

def create_user_if_not_exists(telegram_id: int, username: str, conn=None) -> bool:
    """
    Создание нового пользователя, если пользователь с таким telegram_id не существует.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cur = conn.cursor()
    
    try:
        cur.execute("""
        SELECT user_id FROM users WHERE telegram_id = %s
        """, (telegram_id,))
        
        if cur.fetchone() is None:
            cur.execute("""
            INSERT INTO users (telegram_id, username)
            VALUES (%s, %s)
            """, (telegram_id, username))
            print(f"Создан новый пользователь с telegram_id {telegram_id}")
        else:
            print(f"Пользователь с telegram_id {telegram_id} уже существует")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Ошибка при проверке/создании пользователя: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        if should_close:
            conn.close()