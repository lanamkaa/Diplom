from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from .common import cancel
from .states import WAITING_FOR_QUESTION
from ..yandexgpt import yandex_gpt_query
from .ask_gpt_workflow import ask_gpt_workflow, rate_answer
from ..database.users.get_user import get_user_by_telegram_id
from ..database.users.update_last_active import update_last_active_at
from ..database.users.create_user import create_user_if_not_exists

async def start_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /ask.
    Запрашивает у пользователя вопрос для GPT.
    """
    # Очищаем предыдущие данные, кроме истории сообщений
    if 'messages' not in context.user_data:
        context.user_data['messages'] = []
    else:
        # Очищаем только текущий вопрос
        context.user_data.pop('current_question_id', None)

    telegram_id = update.effective_user.id
    update_last_active_at(telegram_id)

    await update.message.reply_text(
        "Задайте ваш вопрос, и я постараюсь помочь! 😊\n\n"
        "Если передумаете — просто нажмите /cancel"
    )
    return WAITING_FOR_QUESTION

async def process_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает текст вопроса и получает ответ от YandexGPT.
    """
    telegram_id = update.effective_user.id
    update_last_active_at(telegram_id)

    # Создать пользователя, если не существует
    if not create_user_if_not_exists(telegram_id, update.effective_user.username, update.effective_user.first_name):
        print(f"⚠️ Не удалось проверить/создать пользователя {telegram_id} в базе данных")

    user = get_user_by_telegram_id(telegram_id)
    user_id = user[0]  # Получаем только user_id из кортежа
    user_question = update.message.text

    try:
        # Добавляем вопрос пользователя в историю
        context.user_data['messages'].append({
            "role": "user",
            "text": user_question
        })

        gpt_response, question_type, valid_question = await yandex_gpt_query(user_question, context.user_data['messages'])
        if valid_question:
            print(gpt_response, question_type)
            success, question_id = ask_gpt_workflow(user_id, user_question, gpt_response, question_type)

            if success:
                context.user_data['current_question_id'] = question_id

                # Добавляем ответ GPT в историю
                context.user_data['messages'].append({
                    "role": "assistant",
                    "text": gpt_response
                })

                keyboard = [
                    [
                        InlineKeyboardButton("1 ⭐", callback_data=f"rate_{question_id}_1"),
                        InlineKeyboardButton("2 ⭐", callback_data=f"rate_{question_id}_2"),
                        InlineKeyboardButton("3 ⭐", callback_data=f"rate_{question_id}_3"),
                        InlineKeyboardButton("4 ⭐", callback_data=f"rate_{question_id}_4"),
                        InlineKeyboardButton("5 ⭐", callback_data=f"rate_{question_id}_5"),
                    ],
                    [
                        InlineKeyboardButton("Техническая поддержка", url="https://t.me/find_avrunev_bot"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                # Добавляем историю диалога к ответу
                history_text = "\n\nИстория диалога:\n"
                for msg in context.user_data['messages'][-4:]:  # Показываем последние 2 пары вопрос-ответ
                    role = "Вы" if msg["role"] == "user" else "Бот"
                    history_text += f"{role}: {msg['text']}\n"

                await update.message.reply_text(
                    f"{gpt_response}\n\n"
                    "Пожалуйста, оцените ответ:",
                    reply_markup=reply_markup
                )

                await update.message.reply_text(
                    "Вы можете задать ещё вопрос или ввести /cancel для завершения"
                )
            else:
                await update.message.reply_text(
                    "❌ Ошибка при сохранении ответа.\n"
                    "Попробуйте снова или используйте /cancel."
                )
        else:
            await update.message.reply_text(
                "Этот вопрос вне моей компетенции, но я с радостью помогу с другими темами! 💡\n\n"
                "Попробуйте снова или используйте /cancel."
            )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Произошла ошибка: {str(e)}\n"
            "Попробуйте снова или используйте /cancel."
        )

    return WAITING_FOR_QUESTION

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обрабатывает оценку ответа пользователя.
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
            "❌ Ошибка при сохранении оценки."
        )

    return WAITING_FOR_QUESTION

ask_handler = ConversationHandler(
    entry_points=[CommandHandler("ask", start_ask)],
    states={
        WAITING_FOR_QUESTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_question),
            CallbackQueryHandler(handle_rating, pattern=r"^rate_\d+_[1-5]$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=True,
)