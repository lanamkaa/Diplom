from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters
from util import *

FEEDBACK_TEXT = range(1)
async def feedback(update, context):
    feedback_text = update.message.text.replace("/feedback", "").strip()

    if feedback_text:
        await context.bot.send_message(
            chat_id=888737841,
            text=f"Новый фидбэк от @{update.effective_user.username or 'анонимного пользователя'}:\n\n{feedback_text}"
        )
        await update.message.reply_text("Спасибо за Вашу обратную связь! Она была отправлена. Прекрасного Вам дня! ✨️")
        return ConversationHandler.END

    await send_photo(update, context, "картинка3")
    await update.message.reply_text(
        "Напишите, пожалуйста, Вашу обратную связь. Мы с радостью примем Ваши замечания и предложения! 😊\n\nДля отмены действия - /cancel"
    )
    return FEEDBACK_TEXT

async def feedback_response(update, context):
    feedback_text = update.message.text
    await context.bot.send_message(
        chat_id=888737841,
        text=f"Новый фидбэк от @{update.effective_user.username or 'анонимного пользователя'}:\n\n{feedback_text}"
    )
    await update.message.reply_text("Спасибо за Вашу обратную связь! Она была отправлена. Прекрасного Вам дня! ✨️")
    return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text("Вернуться в /menu")
    return ConversationHandler.END

feedback_handler = ConversationHandler(
    entry_points=[CommandHandler("feedback", feedback)],
    states={
        FEEDBACK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, feedback_response)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)