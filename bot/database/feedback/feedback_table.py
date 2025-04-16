from ..connect import get_db_connection

def create_feedback_table(conn=None):
    """
    Создание таблицы feedback, если она не существует.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cur = conn.cursor()
    
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            question_id INTEGER,
            is_dialog_feedback BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("Таблица feedback создана успешно")
        
    except Exception as e:
        print(f"Ошибка при создании таблицы feedback: {e}")
        conn.rollback()
    finally:
        cur.close()
        if should_close:
            conn.close()
