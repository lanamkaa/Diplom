from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from ..command_logic import handle_command_input
from ..database.users.update_last_active import update_last_active_at

async def handle_plain_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик текстовых сообщений без команды.
    Пытается распознать команду по ключевым словам, опечаткам и раскладке.
    """
    context.user_data.clear()

    telegram_id = update.effective_user.id
    update_last_active_at(telegram_id)

    user_input = update.message.text
    response = handle_command_input(user_input)

    await update.message.reply_text(response)

    return ConversationHandler.END
