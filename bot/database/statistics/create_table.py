from ..connect import get_db_connection

def create_link_statistics_table(conn=None):
    """
    Создание таблицы link_statistics, если она не существует. 
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
        
    cur = conn.cursor()
    
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS link_statistics (
            stat_id SERIAL PRIMARY KEY,
            url TEXT NOT NULL,
            processing_time FLOAT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("Таблица link_statistics создана успешно")
        
    except Exception as e:
        print(f"Ошибка при создании таблицы link_statistics: {e}")
        conn.rollback()
    finally:
        cur.close()
        if should_close:
            conn.close()

