from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from ..utils.scraping import get_links
from ..database.users.update_last_active import update_last_active_at
from ..database.users.create_user import create_user_if_not_exists

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /services.
    Показывает список сервисов НГТУ в виде кнопок.
    """
    context.user_data.clear()

    telegram_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    update_last_active_at(telegram_id)

   # Создать пользователя, если не существует
    if not create_user_if_not_exists(telegram_id, username, first_name):
        print(f"⚠️ Не удалось проверить/создать пользователя {telegram_id} в базе данных")


    links = get_links()

    keyboard = [
        [InlineKeyboardButton(name, url=url)] for name, url in links
    ]

    await update.message.reply_text(
        text=(
            "🗂️ <b>Доступные цифровые сервисы НГТУ</b>\n\n"
            "Выберите нужный сервис из списка ниже.\n"
            "Для перехода просто нажмите на соответствующую кнопку."
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

    return ConversationHandler.END
