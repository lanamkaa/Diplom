from ..connect import get_db_connection

def create_questions_table(conn=None):
    """
    Создание таблицы questions, если она не существует.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    if conn is None:
        print("Ошибка: Не удалось установить подключение к базе данных")
        return False
        
    cur = conn.cursor()
    
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            question_id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
            question TEXT NOT NULL,
            answer_text TEXT,
            answer_rating INTEGER CHECK (answer_rating IS NULL OR (answer_rating >= 1 AND answer_rating <= 5)),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("Таблица questions создана успешно")
        return True
        
    except Exception as e:
        print(f"Ошибка при создании таблицы questions: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        if should_close:
            conn.close()
