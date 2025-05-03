from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes, JobQueue
import logging
from telegram import Update
from bot.database.connect import get_db_connection
from dotenv import load_dotenv
from typing import Optional
import os
import sys
import unicodedata
from bot.database.init import initialize_database
from bot.handlers.start import start
from bot.handlers.help import help
from bot.handlers.services import services
from bot.handlers.feedback import handle_feedback, handle_feedback_comment, handle_feedback_callback
from bot.handlers.common import cancel
from bot.handlers.ask import start_ask, process_question, handle_rating
from bot.handlers.check_link import check_link_response, check_link
from bot.handlers.states import FEEDBACK_RATING, FEEDBACK_COMMENT, WAITING_FOR_QUESTION, CHECK_LINK_TEXT
from bot.handlers.profile import profile

load_dotenv()

ADMIN_IDS = [888737841]
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
        
#async def error_handler(update, context):
#    """Журнал ошибок"""
#    logger.warning('Обновление "%s" вызвало ошибку "%s"', update, context.error)
#    try:
#        if update and update.effective_message:
#            await update.effective_message.reply_text(
#                "Извините, произошла ошибка. Пожалуйста, попробуйте позже."
#            )
#    except Exception as e:
#        logger.error(f"Ошибка в обработчике ошибок: {e}")

def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    job_queue = JobQueue()
    job_queue.set_application(app)

    conv = ConversationHandler(
        entry_points=[  
           CommandHandler("feedback", handle_feedback),
           CommandHandler("ask", start_ask),
           CommandHandler("check_link", check_link),
        ],
        states={
            FEEDBACK_RATING: [
                CallbackQueryHandler(handle_feedback_callback, pattern="^feedback_"),
            ],
            FEEDBACK_COMMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback_comment),
            ],
            WAITING_FOR_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_question),
                CallbackQueryHandler(handle_rating, pattern=r"^rate_\d+_[1-5]$"),
            ],
            CHECK_LINK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_link_response)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),  
            CommandHandler("start", start),
            CommandHandler("services", services),
            CommandHandler("help", help),
        ],  
        allow_reentry=True,
        per_message=False,
        per_user=True,
        per_chat=True
    )

    app.add_handler(conv)

    #app.add_handler(CommandHandler("start", start))
    #app.add_handler(CommandHandler("services", services))
    app.add_handler(CommandHandler("help", help))
    #app.add_handler(CommandHandler("profile", profile))


    #app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_plain_text))
    #app.add_handler(MessageHandler(filters.COMMAND, handle_plain_text))  # чтобы ловить опечатки в командах
    #app.job_queue.run_repeating(send_reminders, interval=86400, first=60)
    #app.job_queue.run_repeating(send_reminders, interval=180, first=10) # проверка


    initialize_database() # для создания таблиц при включении бота
    
#    app.add_error_handler(error_handler)

    print("Бот запущен...")

    app.run_polling()

if __name__ == "__main__":
    main()
