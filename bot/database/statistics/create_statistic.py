from typing import Optional
from ..connect import get_db_connection

def create_link_statistic(url: str, processing_time: float) -> Optional[int]:
    """
    Создание новой записи статистики проверки ссылки в базе данных.
    
    Args:
        url (str): Ссылка, которая была проверена
        processing_time (float): Время, затраченное на обработку URL в секундах
        
    Returns:
        Optional[int]: ID созданной записи статистики
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO link_statistics (url, processing_time)
            VALUES (%s, %s)
            RETURNING stat_id
            """,
            (url, processing_time)
        )
        
        stat_id = cur.fetchone()[0]
        conn.commit()
        return stat_id
        
    except Exception as e:
        print(f"Ошибка при создании записи статистики: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
