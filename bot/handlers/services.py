from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from ..utils.scraping import get_links
from ..database.users.update_last_active import update_last_active_at

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /services.
    Показывает список сервисов НГТУ в виде кнопок.
    """
    context.user_data.clear()

    telegram_id = update.effective_user.id
    update_last_active_at(telegram_id)

    links = get_links()

    keyboard = [
        [InlineKeyboardButton(name, url=url)] for name, url in links
    ]

    await update.message.reply_text(
        text=(
            "🗂️ *Сервисы НГТУ*\n\n"
            "Выберите интересующий вас сервис из списка ниже:\n"
            "Нажмите на кнопку для перехода\\."
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )

    return ConversationHandler.END
