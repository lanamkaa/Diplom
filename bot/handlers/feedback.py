from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from ..database.feedback.create_feedback import create_feedback
from .common import cancel


# Create conversation handler for feedback
FEEDBACK_RATING, FEEDBACK_COMMENT = range(2)

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the feedback command and show rating options.
    """
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
        "How would you rate your experience?",
        reply_markup=reply_markup
    )

    return FEEDBACK_RATING

async def handle_feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the feedback callback when a user selects a rating.
    """
    query = update.callback_query
    await query.answer()
    
    # Extract rating from callback data
    rating = int(query.data.split('_')[1])
    
    # Store rating in context for later use
    context.user_data['last_rating'] = rating
    
    # Get user info
    user_id = query.from_user.id
    
    # Store feedback in database
    success = create_feedback(
        user_id=user_id,
        rating=rating,
        is_dialog_feedback=True
    )
    
    if success:
        await query.edit_message_text(
            f"Thank you for your {rating} star rating! "
            "Would you like to add a comment to your feedback? "
            "Please type your comment or use /cancel to skip."
        )
    else:
        await query.edit_message_text(
            "Sorry, there was an error saving your feedback. "
            "Please try again later."
        )
        return ConversationHandler.END
    
    return FEEDBACK_COMMENT

async def handle_feedback_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle additional feedback comments from users.
    """
    user_id = update.message.from_user.id
    comment = update.message.text
    
    # Store feedback with comment
    success = create_feedback(
        user_id=user_id,
        rating=context.user_data.get('last_rating', 0),
        comment=comment,
        is_dialog_feedback=True
    )
    
    if success:
        await update.message.reply_text(
            "Thank you for your detailed feedback! "
            "We appreciate you taking the time to help us improve."
        )
    else:
        await update.message.reply_text(
            "Sorry, there was an error saving your feedback. "
            "Please try again later."
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