from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from ..utils.util import escape_markdown
from ..database.users.get_user import get_user_by_telegram_id
from ..database.users.update_last_active import update_last_active_at


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработчик команды /profile.
    Отправляет пользователю его профиль: имя, username и даты активности.
    """
    context.user_data.clear()

    telegram_id = update.effective_user.id
    user = get_user_by_telegram_id(telegram_id)

    if user:
        user_id, username, first_name, created_at, last_active_at = user

        first_name = escape_markdown(first_name or "Не указано")
        username = escape_markdown(username or "Не указано")
        created_at_str = escape_markdown(created_at.strftime('%d.%m.%Y %H:%M') if created_at else "Неизвестно")
        last_active_str = escape_markdown(last_active_at.strftime('%d.%m.%Y %H:%M') if last_active_at else "Неизвестно")

        profile_text = (
            "👤 *Ваш профиль:*\n\n"
            f"*Имя:* {first_name}\n"
            f"*Username:* @{username}\n"
            f"*Дата регистрации:* {created_at_str}\n"
            f"*Последняя активность:* {last_active_str}"
        )
    else:
        profile_text = (
            "😔 *Профиль не найден.*\n"
            "Пожалуйста, начните с команды /start."
        )

    await update.message.reply_text(profile_text, parse_mode=ParseMode.MARKDOWN_V2)
    update_last_active_at(telegram_id)

    return ConversationHandler.END