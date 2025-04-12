async def cancel(update, context):
    await update.message.reply_text("Вернуться в /menu")
    return ConversationHandler.END
    