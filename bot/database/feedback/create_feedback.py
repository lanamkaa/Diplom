from typing import Optional
from ..connect import get_db_connection

def create_feedback(
    user_id: int,
    rating: int,
    comment: Optional[str] = None,
    question_id: Optional[int] = None,
    is_dialog_feedback: bool = False
) -> bool:
    """
    Создание новой записи в таблице feedback.
    
    Args:
        user_id (int): ID пользователя, который оставил отзыв
        rating (int): Оценка (1-5)
        comment (Optional[str]): Опциональный комментарий
        question_id (Optional[int]): Опциональный ID вопроса, к которому относится отзыв
        is_dialog_feedback (bool): True, если это отзыв за весь диалог, False - если за отдельный вопрос
    """
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO feedback (user_id, rating, comment, question_id, is_dialog_feedback)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, rating, comment, question_id, is_dialog_feedback))
            
            conn.commit()
            print("Создана новая запись в таблице feedback")
            return True
            
    except Exception as e:
        print(f"Ошибка при создании записи в таблице feedback: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close() 