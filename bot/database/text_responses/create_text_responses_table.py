from ..connect import get_db_connection

def create_text_responses_table(conn=None):
    """
    Создание таблицы text_responses, если она не существует.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cur = conn.cursor()
    
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS text_responses (
            text_response_id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
            response_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("Таблица text_responses создана успешно")
        
    except Exception as e:
        print(f"Ошибка при создании таблицы text_responses: {e}")
        conn.rollback()
    finally:
        cur.close()
        if should_close:
            conn.close()
