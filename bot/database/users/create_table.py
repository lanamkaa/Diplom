from ..connect import get_db_connection

def create_user_table(conn=None):
    """
    Создание таблицы users, если она не существует.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cur = conn.cursor()
    
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            username VARCHAR(100),
            first_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_reminder_sent_at TIMESTAMP
        )
        """)

        conn.commit()
        print("Таблица users создана успешно")
        
    except Exception as e:
        print(f"Ошибка при создании таблицы users: {e}")
        conn.rollback()
    finally:
        cur.close()
        if should_close:
            conn.close()
