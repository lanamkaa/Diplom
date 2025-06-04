from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from ..database.users.get_user import get_user_by_telegram_id
from ..database.users.update_last_active import update_last_active_at
from ..database.users.update_reminder_status import update_reminder_status
from ..handlers.reminders import send_reminders
from ..database.users.create_user import create_user_if_not_exists
from babel.dates import format_datetime
import logging

logger = logging.getLogger(__name__)

def format_date_russian(date):
    """Format date in Russian style: '4 марта 2025 13:16'"""
    if not date:
        return "Неизвестно"
    return format_datetime(date, format='d MMMM YYYY HH:mm', locale='ru')

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /profile.
    Показывает профиль пользователя и настройки.
    """
    telegram_id = update.effective_user.id
    logger.info(f"Profile command received from user {telegram_id}")

    # Создать пользователя, если не существует
    if not create_user_if_not_exists(telegram_id, update.effective_user.username, update.effective_user.first_name):
        logger.error(f"⚠️ Не удалось проверить/создать пользователя {telegram_id} в базе данных")
        await update.message.reply_text("❌ Произошла ошибка при получении профиля. Пожалуйста, попробуйте позже.")
        return

    user = get_user_by_telegram_id(telegram_id)
    if not user:
        await update.message.reply_text("❌ Пользователь не найден.")
        return

    update_last_active_at(telegram_id)

    # Создаем клавиатуру с кнопкой переключения напоминаний
    keyboard = [
        [
            InlineKeyboardButton(
                "🔔 Напоминания: " + ("Включены" if user[5] else "Выключены"),
                callback_data="toggle_reminders"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    created_at_str = format_datetime(user[3], format='d MMMM YYYY HH:mm', locale='ru') if user[3] else "Неизвестно"
    last_active_str = format_datetime(user[4], format='d MMMM YYYY HH:mm', locale='ru') if user[4] else "Неизвестно"

    await update.message.reply_text(
        f"👤 Ваш профиль:\n\n"
        f"ID: {user[0]}\n"
        f"Telegram ID: {telegram_id}\n"
        f"Username: @{user[1]}\n"
        f"Имя: {user[2]}\n"
        f"Дата регистрации: {created_at_str}\n"
        f"Последняя активность: {last_active_str}\n\n"
        f"Настройки:",
        reply_markup=reply_markup
    )

async def handle_reminder_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает переключение статуса напоминаний.
    """
    query = update.callback_query
    logger.info(f"Reminder toggle callback received: {query.data}")
    await query.answer()

    telegram_id = update.effective_user.id
    user = get_user_by_telegram_id(telegram_id)
    
    if not user:
        logger.error(f"User {telegram_id} not found when trying to toggle reminders")
        await query.edit_message_text("❌ Ошибка: пользователь не найден.")
        return

    # Получаем текущий статус и инвертируем его
    current_status = user[5]  # reminder_enabled находится в 6-м элементе кортежа
    new_status = not current_status
    logger.info(f"Toggling reminders for user {telegram_id} from {current_status} to {new_status}")
    
    # Обновляем статус в базе данных
    if update_reminder_status(telegram_id, new_status):
        # Обновляем клавиатуру
        keyboard = [
            [
                InlineKeyboardButton(
                    "🔔 Напоминания: " + ("Включены" if new_status else "Выключены"),
                    callback_data="toggle_reminders"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        created_at_str = format_datetime(user[3], format='d MMMM YYYY HH:mm', locale='ru') if user[3] else "Неизвестно"
        last_active_str = format_datetime(user[4], format='d MMMM YYYY HH:mm', locale='ru') if user[4] else "Неизвестно"
        
        # Обновляем сообщение
        await query.edit_message_text(
            f"👤 Ваш профиль:\n\n"
            f"ID: {user[0]}\n"
            f"Telegram ID: {telegram_id}\n"
            f"Username: @{user[1]}\n"
            f"Имя: {user[2]}\n"
            f"Дата регистрации: {created_at_str}\n"
            f"Последняя активность: {last_active_str}\n\n"
            f"Настройки:",
            reply_markup=reply_markup
        )
        
        # Обновляем статус напоминаний в job_queue
        if new_status:
            # Проверяем, нет ли уже запущенного job'а
            job_exists = False
            for job in context.job_queue.jobs():
                if job.name == 'send_reminders':
                    job_exists = True
                    break
            
            if not job_exists:
                context.job_queue.run_repeating(
                    send_reminders,
                    interval=3600,  # каждый час
                    first=10,  # первое выполнение через 10 секунд
                    name='send_reminders'
                )
                logger.info(f"Started reminder job for user {telegram_id}")
        else:
            # Удаляем job, если он существует
            for job in context.job_queue.jobs():
                if job.name == 'send_reminders':
                    job.schedule_removal()
                    logger.info(f"Removed reminder job for user {telegram_id}")
    else:
        logger.error(f"Failed to update reminder status for user {telegram_id}")
        await query.edit_message_text("❌ Ошибка при обновлении настроек.")

# Создаем обработчики
profile_command = CommandHandler("profile", profile)
reminder_toggle = CallbackQueryHandler(handle_reminder_toggle, pattern="toggle_reminders")

