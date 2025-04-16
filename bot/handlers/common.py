from telegram.ext import ConversationHandler

async def cancel(update, context):
    """Обработчик команды /cancel для диалогов"""
    # Очищаем данные диалога
    context.user_data.clear()
    
    await update.message.reply_text("Вы отменили действие.\nВернуться в /start")
    return ConversationHandler.END