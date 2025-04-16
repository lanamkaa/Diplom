from typing import Optional, Dict, List, Tuple
from ..connect import get_db_connection

def get_url_statistics(url: str, detailed: bool = False) -> Dict:
    """
    Получение статистики для конкретной ссылки из таблицы link_statistics.
    
    Args:
        url: Ссылка для запроса статистики
        detailed: Если True, возвращает дополнительную статистику, включая среднее время обработки
                 Если False, возвращает только количество вхождений
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if not detailed:
            cur.execute(
                "SELECT COUNT(*) FROM link_statistics WHERE url = %s",
                (url,)
            )
            count = cur.fetchone()[0]
            return {"count": count}
        else:
            cur.execute("""
                SELECT 
                    COUNT(*) as count,
                    AVG(processing_time) as avg_time,
                    MIN(created_at) as first_seen,
                    MAX(created_at) as last_seen
                FROM link_statistics 
                WHERE url = %s
                GROUP BY url
            """, (url,))
            
            result = cur.fetchone()
            if result:
                count, avg_time, first_seen, last_seen = result
                return {
                    "count": count,
                    "avg_processing_time": round(avg_time, 3),
                    "first_seen": first_seen,
                    "last_seen": last_seen
                }
            return {
                "count": 0,
                "avg_processing_time": 0,
                "first_seen": None,
                "last_seen": None
            }
            
    finally:
        cur.close()
        conn.close()