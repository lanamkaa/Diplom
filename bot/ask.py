from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters
from yandexgpt import yandex_gpt_query
from util import *


async def ask(update: Update, context):
    await send_text_buttons(update, context, "Какой у вас вопрос?) ", {
            "main_menu": "Завершить",
    })
    return ConversationHandler.END

ASK_RESPONSE = range(1)

async def ask_response(update: Update, context):
    user_question = update.message.text

    try:
        gpt_response = await yandex_gpt_query(user_question)
        await update.message.reply_text(f"{gpt_response}\n\nДля отмены действия - /cancel")

    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

    return ASK_RESPONSE
async def cancel(update, context):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

ask_handler = ConversationHandler(
    entry_points=[CommandHandler("ask", ask_response)],
    states={
        ASK_RESPONSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_response)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)