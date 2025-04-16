from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..utils.scraping import get_links

async def services(update, context):
    links = get_links()
    keyboard = [
        [InlineKeyboardButton(name, url=url)] for name, url in links
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "*Сервисы НГТУ 🗂️*\n\n"
        "Нажмите на понравившийся сервис, чтобы узнать о нём подробнее.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
