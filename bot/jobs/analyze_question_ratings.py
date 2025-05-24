from datetime import datetime, timedelta
from bot.database.connect import get_db_connection
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from bot.database.users.create_user import create_user_if_not_exists
import logging

ADMIN_IDS = [888737841, 344532317]

logger = logging.getLogger(__name__)

async def analyze_question_ratings(context: ContextTypes.DEFAULT_TYPE):
    """
    Анализирует вопросы за последнюю неделю, группирует их по question_type
    и выявляет группу с самой низкой answer_rating.
    """
    try:
        logger.info("Starting analyze_question_ratings job")
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
                WHERE created_at >= %s 
                AND answer_rating IS NOT NULL
                GROUP BY question_type
                ORDER BY avg_rating ASC
            """, (week_ago,))
            
            results = cur.fetchall()
            
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
                
                # Создаем кнопку для просмотра деталей
                keyboard = [[InlineKeyboardButton("📋 Показать детали вопросов", callback_data="show_questions_details")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Отправляем сообщение администраторам
                for admin_id in ADMIN_IDS:
                    try:
                        await context.bot.send_message(
                            chat_id=admin_id,
                            text=message,
                            reply_markup=reply_markup
                        )
                        logger.info(f"Successfully sent analysis to admin {admin_id}")
                    except Exception as e:
                        logger.error(f"Ошибка при отправке сообщения администратору {admin_id}: {e}")
            else:
                logger.info("Нет данных о вопросах за последнюю неделю")
                
        except Exception as e:
            logger.error(f"Ошибка при анализе вопросов: {e}")
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        logger.error(f"Critical error in analyze_question_ratings: {e}")

async def show_questions_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик нажатия на кнопку "Показать детали вопросов".
    Показывает вопросы по одному с кнопкой "Следующий".
    """
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("У вас нет доступа к этой функции.")
        return
    
    try:
        # Получаем текущий индекс из callback_data или устанавливаем 0
        current_index = 0
        if query.data != "show_questions_details":
            current_index = int(query.data.split("_")[-1])
        
        conn = get_db_connection()
        if not conn:
            await query.edit_message_text("Ошибка подключения к базе данных.")
            return
            
        cur = conn.cursor()
        try:
            week_ago = datetime.now() - timedelta(days=7)
            
            # Получаем все вопросы за последнюю неделю с ответами и оценками
            cur.execute("""
                SELECT 
                    question,
                    answer_text,
                    answer_rating,
                    question_type,
                    created_at
                FROM questions 
                WHERE created_at >= %s 
                AND answer_rating IS NOT NULL
                ORDER BY answer_rating ASC, created_at DESC
            """, (week_ago,))
            
            questions = cur.fetchall()
            
            if questions:
                if current_index >= len(questions):
                    await query.edit_message_text("Это был последний вопрос.")
                    return
                
                question, answer, rating, q_type, created_at = questions[current_index]
                
                message = (
                    f"📋 Вопрос {current_index + 1} из {len(questions)}:\n\n"
                    f"❓ Вопрос: {question}\n"
                    f"📝 Ответ: {answer}\n"
                    f"⭐ Оценка: {rating}\n"
                    f"📌 Тип: {q_type}\n"
                    f"🕒 Дата: {created_at.strftime('%Y-%m-%d %H:%M')}\n"
                )
                
                # Создаем кнопки навигации
                keyboard = []
                nav_buttons = []
                
                # Добавляем кнопку "Предыдущий" если это не первый вопрос
                if current_index > 0:
                    nav_buttons.append(InlineKeyboardButton("⬅️ Предыдущий", callback_data=f"show_questions_details_{current_index - 1}"))
                
                # Добавляем кнопку "Следующий" если есть еще вопросы
                if current_index + 1 < len(questions):
                    nav_buttons.append(InlineKeyboardButton("➡️ Следующий", callback_data=f"show_questions_details_{current_index + 1}"))
                
                if nav_buttons:
                    keyboard.append(nav_buttons)
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=message,
                    reply_markup=reply_markup
                )
            else:
                await query.edit_message_text("Нет данных о вопросах за последнюю неделю.")
                
        except Exception as e:
            logger.error(f"Ошибка при получении деталей вопросов: {e}")
            await query.edit_message_text("Произошла ошибка при получении данных.")
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"Critical error in show_questions_details: {e}")
        await query.edit_message_text("Произошла критическая ошибка.")

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /analyze для администраторов.
    Запускает анализ вопросов вручную.
    """
    user_id = update.effective_user.id
    telegram_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name

       # Создать пользователя, если не существует
    if not create_user_if_not_exists(telegram_id, username, first_name):
        print(f"⚠️ Не удалось проверить/создать пользователя {telegram_id} в базе данных")



    if user_id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return
    
    await update.message.reply_text("Запускаю анализ вопросов...")
    await analyze_question_ratings(context)
