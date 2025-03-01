from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the main menu."""
    keyboard = [
        [InlineKeyboardButton("Сервисы НГТУ 🗂️", callback_data="show_services")],
        [InlineKeyboardButton("Задать вопрос ❓", callback_data="ask_response")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text="*Главное меню*\nВыберите нужный пункт:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text="*Главное меню*\nВыберите нужный пункт:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
