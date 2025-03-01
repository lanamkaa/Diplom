from util import *

async def main_menu(update, context):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("Выбрать из кнопок", callback_data="show_services")],
        [InlineKeyboardButton("Задать свой вопрос", callback_data="ask_response")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.answer()
    await query.edit_message_text(
        "*Главное меню 🧑‍🏫*\n\n"
        "Выберите нужный пункт:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

