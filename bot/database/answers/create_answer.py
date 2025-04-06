from typing import Optional
from ..connect import get_db_connection

def create_answer(question_id: int, user_id: int, answer_text: str, rating: Optional[int] = None) -> Optional[int]:
    """
    Create a new answer in the database.
    
    Args:
        question_id (int): ID of the question being answered
        user_id (int): ID of the user creating the answer
        answer_text (str): The text content of the answer
        rating (Optional[int]): Optional rating for the answer (1-5)
        
    Returns:
        Optional[int]: The ID of the created answer, or None if creation failed
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            """
            INSERT INTO answers (question_id, user_id, answer_text, rating)
            VALUES (%s, %s, %s, %s)
            RETURNING answer_id
            """,
            (question_id, user_id, answer_text, rating)
        )
        result = cur.fetchone()
        conn.commit()
        return result[0] if result else None
            
    except Exception as e:
        print(f"Error creating answer: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
