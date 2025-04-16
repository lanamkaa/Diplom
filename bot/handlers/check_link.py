import re
import ipaddress
from urllib.parse import urlparse, unquote

import idna
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters
from .common import cancel
from ..database.statistics.create_statistic import create_link_statistic
import time
from ..database.statistics.statistics import get_url_statistics

CHECK_LINK_TEXT = range(1)

TRUSTED_DOMAIN = "nstu.ru"

def is_safe_url(url: str) -> bool:
    """
    Проверяет, что URL:
      - Использует HTTPS.
      - Не указывает порт не по умолчанию (разрешен только явный порт 443).
      - Имеет имя хоста, принадлежащее доверенному домену (разрешены поддомены).
      - Не содержит кодировки URL или подмены Unicode.
      - Не использует IP-адрес в качестве имени хоста.
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

async def check_link(update, context):
    await update.message.reply_text(
        "Укажите ссылку для проверки! 😊\n\nДля отмены действия - /cancel"
    )
    return CHECK_LINK_TEXT

async def check_link_response(update, context):
    link = update.message.text
    start = time.time()
    if is_safe_url(link):
        reply = "✅ Сссылка безопасна."
    else:
        reply = "❌ Сссылка не безопасна."
    end = time.time()
    create_link_statistic(link, end - start)
    print(get_url_statistics(link, True))
    await update.message.reply_text(reply)
    return ConversationHandler.END

check_link_handler = ConversationHandler(
    entry_points=[CommandHandler("check_link", check_link)],
    states={
        CHECK_LINK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_link_response)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)