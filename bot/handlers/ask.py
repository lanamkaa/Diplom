from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from bot.handlers.feedback import cancel
from ..yandexgpt import yandex_gpt_query

# Define states
ASK_RESPONSE = range(1)
 
async def ask_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user_question = update.message.text
        try:
            gpt_response = await yandex_gpt_query(user_question)
            await update.message.reply_text(f"{gpt_response}\n\nДля отмены действия - /cancel")

        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка: {str(e)}")
    else: 
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("Здравствуйте! Чем могу помочь?\n\nДля отмены действия - /cancel")
    return ASK_RESPONSE

#async def cancel(update, context):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

# Create the conversation handler
ask_handler = ConversationHandler(
    entry_points=[CommandHandler("ask", ask_gpt)],
    states={
        ASK_RESPONSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gpt)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=False  
)
