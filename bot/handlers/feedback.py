from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from ..database.feedback.create_feedback import create_feedback
from .common import cancel

FEEDBACK_RATING, FEEDBACK_COMMENT = range(2)

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает обратную связь и рейтинг.
    """
    context.user_data['conversation_active'] = True
    keyboard = [
        [
            InlineKeyboardButton("1 ⭐", callback_data="feedback_1"),
            InlineKeyboardButton("2 ⭐", callback_data="feedback_2"),
            InlineKeyboardButton("3 ⭐", callback_data="feedback_3"),
            InlineKeyboardButton("4 ⭐", callback_data="feedback_4"),
            InlineKeyboardButton("5 ⭐", callback_data="feedback_5"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Как вам взаимодействие с ботом?",
        reply_markup=reply_markup
    )

    return FEEDBACK_RATING

async def handle_feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обрабатывается обратный вызов обратной связи, когда пользователь выбирает рейтинг.
    """
    query = update.callback_query
    await query.answer()
    
    # Извлечение рейтинга из данных обратного вызова
    rating = int(query.data.split('_')[1])
    
    # Сохранение рейтинга в контексте для последующего использования
    context.user_data['last_rating'] = rating
    
    # Получение информации о пользователе
    user_id = query.from_user.id
    
    # Сохранение обратной связи в базе данных
    success = create_feedback(
        user_id=user_id,
        rating=rating,
        is_dialog_feedback=True
    )
    
    if success:
        await query.edit_message_text(
            f"Спасибо за {rating} ⭐!\n\n"
            "Хотите оставить полный feedback?\n"
            "Пожалуйста, напиши ваш отзыв или используйте /cancel для завершения"
        )
    else:
        await query.edit_message_text(
            "Произошла ошибка при сохранении обратной связи. "
            "Пожалуйста, попробуйте еще раз."
        )
        return ConversationHandler.END
    
    return FEEDBACK_COMMENT

async def handle_feedback_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обрабатывает дополнительные комментарии обратной связи от пользователей.
    """
    user_id = update.message.from_user.id
    comment = update.message.text
    
    # Сохранение обратной связи с комментарием
    success = create_feedback(
        user_id=user_id,
        rating=context.user_data.get('last_rating', 0),
        comment=comment,
        is_dialog_feedback=True
    )
    
    if success:
        await update.message.reply_text(
            "Спасибо за ваш подробный отзыв! "
            "Вы помогаете нам стать лучше."
        )
    else:
        await update.message.reply_text(
            "Произошла ошибка при сохранении обратной связи. "
            "Пожалуйста, попробуйте еще раз."
        )
    
    return ConversationHandler.END

feedback_handler = ConversationHandler(
    entry_points=[CommandHandler("feedback", handle_feedback)],
    states={
        FEEDBACK_RATING: [
            CallbackQueryHandler(handle_feedback_callback, pattern="^feedback_"),
        ],
        FEEDBACK_COMMENT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback_comment),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)