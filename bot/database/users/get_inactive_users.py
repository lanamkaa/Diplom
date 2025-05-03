from ..connect import get_db_connection

def get_inactive_users(days=7):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT telegram_id FROM users
            WHERE last_active_at < NOW() - INTERVAL %s
              AND last_reminder_sent_at IS NULL
        """, (f'{days} days',))
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Ошибка при получении неактивных пользователей: {e}")
        return []
    finally:
        cur.close()
        conn.close()