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
    Create a new feedback entry in the database.
    
    Args:
        user_id (int): Telegram user ID
        rating (int): Rating value (typically 1-5)
        comment (Optional[str]): Optional feedback comment
        question_id (Optional[int]): Optional ID of the question being rated
        is_dialog_feedback (bool): Whether this is feedback for an entire dialog or a single question
        
    Returns:
        bool: True if feedback was successfully created, False otherwise
    """
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        with conn.cursor() as cur:
            # Insert the feedback
            cur.execute("""
                INSERT INTO feedback (user_id, rating, comment, question_id, is_dialog_feedback)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, rating, comment, question_id, is_dialog_feedback))
            
            conn.commit()
            print("Feedback entry created successfully")
            return True
            
    except Exception as e:
        print(f"Error creating feedback: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close() 