from ..connect import get_db_connection

def create_faq_table(conn=None):
    """
    Создание таблицы faq, если она не существует.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cur = conn.cursor()
    
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            faq_id SERIAL PRIMARY KEY,
            question TEXT,
            answer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("Таблица faq создана успешно")
        
    except Exception as e:
        print(f"Ошибка при создании таблицы faq: {e}")
        conn.rollback()
    finally:
        cur.close()
        if should_close:
            conn.close()
