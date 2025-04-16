from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from bot.handlers.feedback import cancel
from ..yandexgpt import yandex_gpt_query
from .ask_gpt_workflow import ask_gpt_workflow, rate_answer
from ..database.users.get_user import get_user_by_telegram_id
from .common import cancel

WAITING_FOR_QUESTION = range(1)
WAITING_FOR_RATING = range(2)

async def start_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handler команды /ask, которая инициирует процесс задавания вопросов.
    """
    await update.message.reply_text(
        "Пожалуйста, введите ваш вопрос!\n\n"
        "Для отмены действия используйте команду /cancel"
    )
    return WAITING_FOR_QUESTION

async def process_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handler для обработки вопроса пользователя и получения ответа GPT.
    """
    try:
        telegram_id = update.message.from_user.id
        user = get_user_by_telegram_id(telegram_id)

        if user is None:
            await update.message.reply_text(
                "Ошибка: пользователь не найден в базе данных.\n"
                "Пожалуйста, начните с команды /start"
            )
            return WAITING_FOR_QUESTION
            
        user_id, _ = user
        user_question = update.message.text
   
        gpt_response = await yandex_gpt_query(user_question)
        success, question_id = ask_gpt_workflow(user_id, user_question, gpt_response)
        
        if success:
            context.user_data['current_question_id'] = question_id

            keyboard = [
                [
                    InlineKeyboardButton("1 ⭐", callback_data=f"rate_{question_id}_1"),
                    InlineKeyboardButton("2 ⭐", callback_data=f"rate_{question_id}_2"),
                    InlineKeyboardButton("3 ⭐", callback_data=f"rate_{question_id}_3"),
                    InlineKeyboardButton("4 ⭐", callback_data=f"rate_{question_id}_4"),
                    InlineKeyboardButton("5 ⭐", callback_data=f"rate_{question_id}_5")
                ],
                [
                    InlineKeyboardButton("техническая поддержка", url="https://t.me/find_avrunev_bot")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"{gpt_response}\n\n"
                "Пожалуйста, оцените ответ от 1 до 5 звезд:",
                reply_markup=reply_markup
            )

            await update.message.reply_text(
                "Вы можете задать следующий вопрос или использовать /cancel для завершения"
            )
            
            return WAITING_FOR_QUESTION
        else:
            await update.message.reply_text(
                "Произошла ошибка при сохранении вопроса и ответа.\n"
                "Пожалуйста, попробуйте еще раз или используйте /cancel для завершения"
            )
            return WAITING_FOR_QUESTION

    except Exception as e:
        await update.message.reply_text(
            f"Произошла ошибка: {str(e)}\n"
            "Пожалуйста, попробуйте еще раз или используйте /cancel для завершения"
        )
        return WAITING_FOR_QUESTION

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handler для обработки оценки ответа пользователем.
    """
    query = update.callback_query
    await query.answer()

    _, question_id, rating = query.data.split('_')
    question_id = int(question_id)
    rating = int(rating)

    success = rate_answer(question_id, rating)
    
    if success:
        await query.edit_message_text(
            f"{query.message.text.split('Пожалуйста, оцените')[0]}\n\n"
            f"Спасибо за вашу оценку: {rating} ⭐!"
        )
    else:
        await query.edit_message_text(
            f"{query.message.text.split('Пожалуйста, оцените')[0]}\n\n"
            "Произошла ошибка при сохранении оценки."
        )
    
    return WAITING_FOR_QUESTION

ask_handler = ConversationHandler(
    entry_points=[CommandHandler("ask", start_ask)],
    states={
        WAITING_FOR_QUESTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_question),
            CallbackQueryHandler(handle_rating, pattern=r"^rate_\d+_[1-5]$")
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=False
)
