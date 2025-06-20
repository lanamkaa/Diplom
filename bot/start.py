from util import *

async def start(update, context):
    text = load_message("main")

    await send_photo(update, context, "картинка1")
    await send_text(update, context, text)
    await send_text(update, context, "Нажмите на /menu")

    await show_main_menu(update,context, {
        "start": "О нас 🧑‍🏫",
        "menu": "Главное меню 😇",
        "services": "Список сервисов 🗂️",
        "ask": "Задай вопрос ❔",
        "help": "Помощь 🤓",
        "feedback": "Обратная связь ❗"
    })