from telegram import Update
from telegram.ext import ContextTypes

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    Доступные команды:
    /start - Начать работу с ботом
    /menu - Показать главное меню
    /help - Показать это сообщение
    /services - Показать сервисы НГТУ
    """
    await update.message.reply_text(help_text)
