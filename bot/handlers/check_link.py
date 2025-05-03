import re
import time
import idna
import ipaddress
from urllib.parse import urlparse, unquote

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from .common import cancel
from .states import CHECK_LINK_TEXT
from ..database.statistics.create_statistic import create_link_statistic
from ..database.statistics.statistics import get_url_statistics
from ..database.users.update_last_active import update_last_active_at

TRUSTED_DOMAIN = "nstu.ru"

def is_safe_url(url: str) -> bool:
    """
    Проверяет безопасность URL.
    Требует HTTPS, проверяет домен, блокирует IP-адреса и подозрительные символы.
    """
    try:
        # Декодирование URL для предотвращения URL-encoding трюков.
        decoded_url = unquote(url)
        parsed = urlparse(decoded_url)

        # Применяем HTTPS.
        if parsed.scheme != "https":
            return False

        # Убедитесь, что есть имя хоста.
        domain = parsed.hostname
        if domain is None:
            return False

        # Нормализация с помощью IDNA кодирования для выявления подделок URL.
        try:
            ascii_domain = idna.encode(domain).decode("ascii").lower()
        except idna.IDNAError:
            return False

        # Отклоняем хосты, содержащие подозрительные последовательности.
        if ".." in ascii_domain or re.search(r"[^a-z0-9\.\-]", ascii_domain):
            return False

        # Блокируем IP-адреса, чтобы предотвратить атаки SSRF.
        try:
            ipaddress.ip_address(ascii_domain)
            return False
        except ValueError:
            pass 

        # Убедитесь, что хост принадлежит доверенной домену.
        # Разрешить, если он точно соответствует доверенной домену или является поддоменом.
        if ascii_domain == TRUSTED_DOMAIN or ascii_domain.endswith("." + TRUSTED_DOMAIN):
            return True

        return False

    except Exception:
        return False

async def check_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /check_link.
    Просит пользователя отправить ссылку для проверки.
    """
    context.user_data.clear()

    telegram_id = update.effective_user.id
    update_last_active_at(telegram_id)

    await update.message.reply_text(
        "🔍 Укажите ссылку для проверки безопасности!\n\nДля отмены используйте /cancel."
    )
    return CHECK_LINK_TEXT

async def check_link_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Проверяет присланную ссылку и сообщает пользователю результат.
    """
    telegram_id = update.effective_user.id
    update_last_active_at(telegram_id)

    link = update.message.text
    start = time.time()

    if is_safe_url(link):
        reply = "✅ Ссылка безопасна."
    else:
        reply = "❌ Ссылка небезопасна."

    end = time.time()
    create_link_statistic(link, end - start)
    print(get_url_statistics(link, detailed=True))

    await update.message.reply_text(reply)
    return ConversationHandler.END

check_link_handler = ConversationHandler(
    entry_points=[CommandHandler("check_link", check_link)],
    states={
        CHECK_LINK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_link_response)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)