from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# Define states
ASK_RESPONSE = 1

async def ask_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the user's question response."""
    try:
        message = update.message.text if update.message else update.callback_query.message.text
        await update.message.reply_text(
            f"Спасибо за ваш вопрос: {message}\nМы ответим вам в ближайшее время.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Вернуться в меню", callback_data="main_menu")
            ]])
        )
        return ConversationHandler.END
    except Exception as e:
        print(f"Error in ask_response: {e}")
        return ConversationHandler.END

async def start_asking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the asking process."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Какой у вас вопрос?",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Отмена", callback_data="cancel")
        ]])
    )
    return ASK_RESPONSE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Отменено. Нажмите кнопку ниже, чтобы вернуться в главное меню.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")
        ]])
    )
    return ConversationHandler.END

# Create the conversation handler
ask_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_asking, pattern="^ask_response$")],
    states={
        ASK_RESPONSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_response)],
    },
    fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")],
    per_message=False  # Changed to False since we're mixing CallbackQueryHandler and MessageHandler
)
