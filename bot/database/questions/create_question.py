from typing import Optional
from ..connect import get_db_connection

def create_question(user_id: int, question: str, answer_id: Optional[int] = None) -> Optional[int]:
    """
    Create a new question in the database.
    
    Args:
        user_id (int): The ID of the user asking the question
        question (str): The question text
        answer_id (Optional[int]): The ID of the answer, if available
        
    Returns:
        Optional[int]: The ID of the created question
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insert the question and return the question_id
        cur.execute(
            """
            INSERT INTO questions (user_id, question, answer_id)
            VALUES (%s, %s, %s)
            RETURNING question_id;
            """,
            (user_id, question, answer_id)
        )
        
        question_id = cur.fetchone()[0]
        conn.commit()
        return question_id
        
    except Exception as e:
        print(f"Error creating question: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
