from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from .common import cancel
from .states import FEEDBACK_RATING, FEEDBACK_COMMENT
from ..database.feedback.create_feedback import create_feedback
from ..database.users.update_last_active import update_last_active_at

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /feedback.
    Запрашивает у пользователя оценку взаимодействия с ботом.
    """
    context.user_data['conversation_active'] = True

    telegram_id = update.effective_user.id
    update_last_active_at(telegram_id)

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

async def handle_feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает оценку пользователя и предлагает оставить отзыв.
    """
    query = update.callback_query
    await query.answer()
    
    rating = int(query.data.split('_')[1])
    context.user_data['last_rating'] = rating
    
    telegram_id = query.from_user.id
    update_last_active_at(telegram_id)

    success = create_feedback(
        user_id=telegram_id,
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

async def handle_feedback_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Сохраняет комментарий пользователя к обратной связи.
    """
    telegram_id = update.effective_user.id
    update_last_active_at(telegram_id)

    comment = update.message.text
    rating = context.user_data.get('last_rating', 0)

    success = create_feedback(
        user_id=telegram_id,
        rating=rating,
        comment=comment,
        is_dialog_feedback=True
    )
    
    if success:
        await update.message.reply_text(
            "Спасибо за ваш подробный отзыв! "
            "Вы помогаете нам стать лучше 😊"
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
