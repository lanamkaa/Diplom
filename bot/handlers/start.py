from telegram import Update
from telegram.ext import ContextTypes
from ..utils.util import *
from ..database.users.create_user import create_user_if_not_exists

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создать пользователя, если он не существует в базе данных
    user = update.effective_user
    if not create_user_if_not_exists(user.id, user.username or user.first_name):
        print(f"Failed to check/create user {user.id} in database")
    print(user)
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
    })
