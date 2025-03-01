from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .main_menu import main_menu
from ..utils.scraping import get_links

async def services(update, context):
    if update.callback_query:
        query = update.callback_query
        data = query.data

        if data == "main_menu":
            await main_menu(update, context)
        else:
            links = get_links()

            keyboard = [
                [InlineKeyboardButton(name, url=url)] for name, url in links
            ]
            keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.answer()
            await query.edit_message_text(
                "*Сервисы НГТУ 🗂️*\n\n"
                "Выберите нужный сервис или вернитесь в главное меню:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    else:
        links = get_links()
        keyboard = [
            [InlineKeyboardButton(name, url=url)] for name, url in links
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "*Сервисы НГТУ 🗂️*\n\n"
            "Выберите нужный сервис или вернитесь в главное меню:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
