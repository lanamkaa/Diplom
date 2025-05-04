from typing import Optional
from ..connect import get_db_connection

def create_question(user_id: int, question: str, answer_text: str = None, answer_rating: int = None, question_type: str = 'general') -> Optional[int]:
    """
    Создание новой записи в таблице questions.
    
    Args:
        user_id (int): ID пользователя, задавшего вопрос
        question (str): Текст вопроса
        answer_text (str, optional): Текст ответа, если доступен
        answer_rating (int, optional): Оценка ответа (1-5), если доступна
        question_type (str, optional): Тип вопроса (default: 'general')
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if conn is None:
            print("Ошибка: Не удалось установить подключение к базе данных")
            return None
            
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO questions (user_id, question, answer_text, answer_rating, question_type)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING question_id
            """,
            (user_id, question, answer_text, answer_rating, question_type)
        )
        
        question_id = cur.fetchone()[0]
        conn.commit()
        
        print(f"Создана новая запись в таблице questions с ID: {question_id}")
        return question_id
        
    except Exception as e:
        print(f"Ошибка при создании записи в таблице questions: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
