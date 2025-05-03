from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from ..utils.util import *
from ..database.users.create_user import create_user_if_not_exists
from ..database.users.update_last_active import update_last_active_at

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start.
    Создаёт пользователя в базе данных (если ещё нет) и показывает главное меню.
    """
    context.user_data.clear()

    telegram_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name

    # Создать пользователя, если не существует
    if not create_user_if_not_exists(telegram_id, username, first_name):
        print(f"⚠️ Не удалось проверить/создать пользователя {telegram_id} в базе данных")

    update_last_active_at(telegram_id)

    text = load_message("main")
    await send_photo(update, context, "картинка1")
    await send_html(update, context, text)

    await show_main_menu(update, context, {
        "start": "Главное меню 🧑‍🏫",
        "services": "Список сервисов 🗂️",
        "ask": "Задай вопрос ❔",
        "help": "Помощь 🤓",
        "feedback": "Обратная связь ❗",
        "check_link": "Проверка ссылки на спам",
        "profile": "Профиль 📊"
    })
    
    return ConversationHandler.END
