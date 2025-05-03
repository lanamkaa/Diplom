from ..connect import get_db_connection

def update_reminder_sent_at(telegram_id: int):
    """
    Обновляет поле last_reminder_sent_at для пользователя после отправки напоминания.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE users
            SET last_reminder_sent_at = CURRENT_TIMESTAMP
            WHERE telegram_id = %s
        """, (telegram_id,))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении last_reminder_sent_at: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()