from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

feedback_handler = ConversationHandler(
    entry_points=[],
    states={},
    fallbacks=[]
)
