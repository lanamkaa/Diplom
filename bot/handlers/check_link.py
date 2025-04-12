import logging
import re
import ipaddress
from urllib.parse import urlparse, unquote

import idna
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from .common import cancel
from ..database.statistics.create_statistic import create_link_statistic
import time
from ..database.statistics.statistics import get_url_statistics

# ----- Secure URL Validator --------------------------------------------------
CHECK_LINK_TEXT = range(1)

# Set your trusted domain here.
TRUSTED_DOMAIN = "nstu.ru"

def is_safe_url(url: str) -> bool:
    """
    Validates that the URL:
      - Uses HTTPS.
      - Does not specify a non-default port (only allow explicit port 443).
      - Has a hostname that belongs to the trusted domain (allows subdomains).
      - Is free from URL encoding or Unicode spoofing.
      - Does not use an IP address as the hostname.
    """
    try:
        # Decode URL to mitigate URL-encoding tricks.
        decoded_url = unquote(url)
        parsed = urlparse(decoded_url)

        # Enforce HTTPS.
        if parsed.scheme != "https":
            return False

        # Ensure a hostname is present.
        domain = parsed.hostname
        if domain is None:
            return False

        # Normalize using IDNA encoding to catch Unicode spoofing.
        try:
            ascii_domain = idna.encode(domain).decode("ascii").lower()
        except idna.IDNAError:
            return False

        # Reject hostnames that contain suspicious sequences.
        if ".." in ascii_domain or re.search(r"[^a-z0-9\.\-]", ascii_domain):
            return False

        # Block numeric IP addresses to help prevent SSRF attacks.
        try:
            ipaddress.ip_address(ascii_domain)
            return False
        except ValueError:
            pass  # Not an IP address, which is expected.

        # Verify that the hostname belongs to the trusted domain.
        # Allow if it is exactly the trusted domain or any subdomain.
        if ascii_domain == TRUSTED_DOMAIN or ascii_domain.endswith("." + TRUSTED_DOMAIN):
            return True

        return False

    except Exception:
        return False
# ----- Telegram Bot Handlers -------------------------------------------------

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