from datetime import datetime, timedelta
from bot.database.connect import get_db_connection
from telegram.ext import ContextTypes
import logging


ADMIN_IDS = [888737841, 344532317]

logger = logging.getLogger(__name__)

async def analyze_question_ratings(context: ContextTypes.DEFAULT_TYPE):
    """
    Анализирует вопросы за последнюю неделю, группирует их по question_type
    и выявляет группу с самой низкой answer_rating.
    """
    conn = get_db_connection()
    if not conn:
        logger.error("Не удалось подключиться к базе данных для анализа вопросов")
        return

    print("Анализ вопросов за последнюю неделю")

    cur = conn.cursor()
    try:
        # Получаем дату неделю назад
        week_ago = datetime.now() - timedelta(days=7)
        
        # Запрос для получения средних оценок по типам вопросов
        cur.execute("""
            SELECT 
                question_type,
                COUNT(*) as question_count,
                AVG(answer_rating) as avg_rating
            FROM questions 
            WHERE answer_rating IS NOT NULL
            AND created_at >= %s
            GROUP BY question_type
            ORDER BY avg_rating ASC
        """, (week_ago,))
        
        results = cur.fetchall()
        print(results)
        if results:
            lowest_rated = results[0]  # Первый результат - с наименьшей оценкой
            message = (
                f"📊 Анализ вопросов за последнюю неделю:\n\n"
                f"Тип вопроса с наименьшей оценкой: {lowest_rated[0]}\n"
                f"Средняя оценка: {lowest_rated[2]:.2f}\n"
                f"Количество вопросов: {lowest_rated[1]}\n\n"
                f"Все типы вопросов:\n"
            )
            
            for q_type, count, rating in results:
                message += f"- {q_type}: {rating:.2f} ({count} вопросов)\n"
            print(message)
            # Отправляем сообщение администраторам
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=message
                    )
                except Exception as e:
                    logger.error(f"Ошибка при отправке сообщения администратору {admin_id}: {e}")
        else:
            logger.info("Нет данных о вопросах за последнюю неделю")
            
    except Exception as e:
        logger.error(f"Ошибка при анализе вопросов: {e}")
    finally:
        cur.close()
        conn.close()
