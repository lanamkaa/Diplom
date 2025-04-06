from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from bot.handlers.feedback import cancel
from ..yandexgpt import yandex_gpt_query
from ..database.questions.create_question import create_question
from ..database.answers.create_answer import create_answer
from ..database.users.get_user import get_user_by_telegram_id


# Define states
ASK_RESPONSE = range(1)
 
async def ask_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user_question = update.message.text
        try:
            # Get user from database
            telegram_id = update.message.from_user.id
            user = get_user_by_telegram_id(telegram_id)
            
            user_id, _ = user  # Unpack user_id from the tuple
            gpt_response = await yandex_gpt_query(user_question)
            question_id = create_question(user_id, user_question)

            # Create the answer in database
            create_answer(question_id, user_id, gpt_response)
            
            await update.message.reply_text(f"{gpt_response}\n\nДля отмены действия - /cancel")

        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка: {str(e)}")
    else: 
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("Здравствуйте! Чем могу помочь?\n\nДля отмены действия - /cancel")
    return ASK_RESPONSE

# Create the conversation handler
ask_handler = ConversationHandler(
    entry_points=[CommandHandler("ask", ask_gpt)],
    states={
        ASK_RESPONSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gpt)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=False  
)
