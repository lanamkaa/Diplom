from typing import Dict, Any
from ..connect import get_db_connection

def update_question(question_id: int, update_data: Dict[str, Any]) -> bool:
    """
    Обновление существующей записи в таблице questions.
    
    Args:
        question_id (int): ID записи, которую нужно обновить
        update_data (Dict[str, Any]): Словарь, содержащий поля для обновления
            Возможные ключи:
            - question: Обновленный текст вопроса
            - answer_text: Обновленный текст ответа
            - answer_rating: Обновленная оценка ответа (1-5)
    """
    if not update_data:
        print("Ошибка: Не предоставлены данные для обновления")
        return False
        
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if conn is None:
            print("Ошибка: Не удалось установить подключение к базе данных")
            return False
            
        cur = conn.cursor()

        set_clauses = []
        values = []
        
        if "question" in update_data:
            set_clauses.append("question = %s")
            values.append(update_data["question"])
            
        if "answer_text" in update_data:
            set_clauses.append("answer_text = %s")
            values.append(update_data["answer_text"])
            
        if "answer_rating" in update_data:
            set_clauses.append("answer_rating = %s")
            values.append(update_data["answer_rating"])
            
        if not set_clauses:
            print("Ошибка: Нет полей для обновления")
            return False

        query = f"""
        UPDATE questions 
        SET {", ".join(set_clauses)}
        WHERE question_id = %s
        """
        
        values.append(question_id)
        
        cur.execute(query, values)

        if cur.rowcount == 0:
            print(f"Ошибка: Не найдена запись с ID: {question_id}")
            return False
            
        conn.commit()
        print(f"Сообщение {question_id} обновлено успешно")
        return True
        
    except Exception as e:
        print(f"Ошибка при обновлении записи: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close() 