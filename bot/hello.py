from util import *

async def menu(update, context):
    await send_text(update, context, "*Привет!) Я ваш персональный помощник по работе с цифровыми сервисами НГТУ*")
    # await send_text(update, context, "Вы написали " + update.message.text) чтобы вывести что написал пользователь
    await send_photo(update, context, "картинка1")
    await send_text_buttons(update, context, "Выберите нужный пункт: ", {
        "show_services": "Выбрать из кнопок",
        "ask_response": "Задать свой вопрос"
    })

