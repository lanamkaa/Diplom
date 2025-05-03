from ..connect import get_db_connection

def update_last_active_at(telegram_id: int):
    """
    Обновляет last_active_at и сбрасывает last_reminder_sent_at в NULL при любом действии пользователя.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE users
            SET last_active_at = CURRENT_TIMESTAMP,
                last_reminder_sent_at = NULL
            WHERE telegram_id = %s
        """, (telegram_id,))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении активности пользователя: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()