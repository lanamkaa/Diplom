from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters
from start import start
from hello import menu
from help import help
from main_menu import main_menu
from ask import ask_response, ask_handler, ASK_RESPONSE
from feedback import cancel, feedback_handler
from scraping import get_links
from util import *

async def services(update, context):
    if update.callback_query:
        query = update.callback_query
        data = query.data

        if data == "main_menu":
            await main_menu(update, context)
        else:
            links = get_links()

            keyboard = [
                [InlineKeyboardButton(name, url=url)] for name, url in links
            ]
            keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.answer()
            await query.edit_message_text(
                "*Сервисы НГТУ 🗂️*\n\n"
                "Выберите нужный сервис или вернитесь в главное меню:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    else:
        links = get_links()
        keyboard = [
            [InlineKeyboardButton(name, url=url)] for name, url in links
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "*Сервисы НГТУ 🗂️*\n\n"
            "Выберите нужный сервис или вернитесь в главное меню:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
async def handle_response(update, context):
    user_response = update.message.text
    await update.message.reply_text(f"Your response: {user_response}")
    return ConversationHandler.END
async def hello_button(update, context):
    query = update.callback_query

    if query.data == "main_menu":
        await main_menu(update, context)
    elif query.data == "show_services":
        await services(update, context)
    elif query.data == "ask_response":
        return await ask_response2(update, context)
    else:
        await query.answer()
        await query.edit_message_text("Пока в процессе")

async def ask_response2(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Какой у вас вопрос?)")
    return ASK_RESPONSE

hello_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(hello_button)],

    states={
        ASK_RESPONSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_response)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
app = ApplicationBuilder().token("7669989730:AAEm76XAyNnjcP7nZFEu-Fsm29CSOPbgxaw").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("services", services))
app.add_handler(CommandHandler("help", help))
app.add_handler(feedback_handler)
app.add_handler(ask_handler)
app.add_handler(hello_handler)
app.add_handler(CallbackQueryHandler(hello_button))


if __name__ == "__main__":
    app.run_polling()

