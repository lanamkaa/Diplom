from telegram import Update
from telegram.ext import ContextTypes
from ..utils.util import *
from ..database.users.create_user import create_user_if_not_exists

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create user if they don't exist in database
    user = update.effective_user
    if not create_user_if_not_exists(user.id, user.username or user.first_name):
        print(f"Failed to check/create user {user.id} in database")
    print(user)
#    User(first_name='Светлана', id=888737841, is_bot=False, language_code='ru', last_name='Мкртчян', username='lanamkaa')
    text = load_message("main")

    await send_photo(update, context, "картинка1")
    await send_text(update, context, text)
    await send_text(update, context, "Нажмите на /menu")

    await show_main_menu(update, context, {
        "start": "О нас 🧑‍🏫",
        "menu": "Главное меню 😇",
        "services": "Список сервисов 🗂️",
        "ask": "Задай вопрос ❔",
        "help": "Помощь 🤓",
        "feedback": "Обратная связь ❗"
    })
