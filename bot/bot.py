from telegram.ext import ApplicationBuilder, CommandHandler
import logging
from bot.database.connect import get_db_connection
from dotenv import load_dotenv
import os
import sys
from bot.database.init import initialize_database
from bot.handlers.start import start
from bot.handlers.help import help
from bot.handlers.ask import ask_handler
from bot.handlers.check_link import check_link_handler
from bot.handlers.services import services
from bot.handlers.feedback import feedback_handler
from bot.handlers.common import cancel

load_dotenv()

# Подключение к базе данных
db = get_db_connection()
if not db:
    print("Не удалось подключиться к базе данных. Проверьте настройки базы данных в файле .env.")
    sys.exit(1)

# Подготовка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update, context):
    """Журнал ошибок"""
    logger.warning('Обновление "%s" вызвало ошибку "%s"', update, context.error)
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Извините, произошла ошибка. Пожалуйста, попробуйте позже."
            )
    except Exception as e:
        logger.error(f"Ошибка в обработчике ошибок: {e}")

def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("services", services))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(feedback_handler)  
    app.add_handler(ask_handler)
    app.add_handler(check_link_handler)

    initialize_database() # для создания таблиц при включении бота
    
    app.add_error_handler(error_handler)

    print("Бот запущен...")
    app.run_polling()
