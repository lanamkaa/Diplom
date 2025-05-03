from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from ..utils.util import *
from ..database.users.update_last_active import update_last_active_at

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /help.
    Отправляет список команд и ссылки на соцмальные сети НГТУ.
    """
    context.user_data.clear()

    telegram_id = update.effective_user.id
    update_last_active_at(telegram_id)

    await send_photo(update, context, "картинка2")
    text = load_message("help")
    await send_text(update, context, text)

    social_text = (
        "🌐 *Наши социальные сети:*\n\n"
        "[ВКонтакте НГТУ](https://vk.com/nstu_vk)\n"
        "[Телеграм НГТУ](https://t.me/nstu_neti)\n"
        "[Одноклассники НГТУ](https://ok.ru/ngtuneti)\n"
        "[Rutube НГТУ](https://rutube.ru/channel/24953858/)\n"
        "[Яндекс.Дзен НГТУ](https://dzen.ru/nstu_neti)\n"
        "[Сайт НГТУ](https://www.nstu.ru)"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=social_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )

    return ConversationHandler.END
