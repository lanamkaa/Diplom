from .connect import get_db_connection
from .users.create_table import create_user_table
from .faq.create_faq_table import create_faq_table
from .questions.create_questions_table import create_questions_table
from .text_responses.create_text_responses_table import create_text_responses_table
from .statistics.create_table import create_link_statistics_table
from .feedback.feedback_table import create_feedback_table
import sys

def initialize_database():
    """
    Инициализация подключения к базе данных и создание таблиц, если они не существуют.
    Возвращает True, если успешно, False в противном случае.
    """
    conn = get_db_connection()
    if not conn:
        print("Не удалось установить подключение к базе данных", file=sys.stderr)
        return False
    
    try:
        create_user_table(conn)
        create_faq_table(conn)
        create_questions_table(conn)
        create_text_responses_table(conn)
        create_link_statistics_table(conn)
        create_feedback_table(conn)
        
        print("Инициализация базы данных завершена успешно")
        return True
    except Exception as e:
        print(f"Ошибка инициализации базы данных: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()
