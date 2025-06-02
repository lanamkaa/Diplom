from ..connect import get_db_connection

def update_reminder_status(telegram_id: int, enabled: bool) -> bool:
    """
    Обновляет статус напоминаний для пользователя.
    
    Args:
        telegram_id: Telegram ID пользователя
        enabled: Новый статус напоминаний
        
    Returns:
        bool: True если обновление успешно, False в случае ошибки
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Обновляем статус напоминаний
        cursor.execute(
            """
            UPDATE users 
            SET reminder_enabled = %s 
            WHERE telegram_id = %s
            """,
            (enabled, telegram_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error updating reminder status: {e}")
        return False 