from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from ..database.users.update_last_active import update_last_active_at

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /cancel.
    Завершает активный диалог и очищает состояние пользователя.
    """
    context.user_data.clear()

    telegram_id = update.effective_user.id
    update_last_active_at(telegram_id)

    await update.message.reply_text("Вы отменили действие.\nВернуться в /start")
    return ConversationHandler.END
    