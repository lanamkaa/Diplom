from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters
import logging
from bot.database.connect import get_db_connection
from dotenv import load_dotenv
import os
import sys
from bot.database.init import initialize_database
# Import handlers
from bot.handlers.start import start
from bot.handlers.help import help
from bot.handlers.main_menu import main_menu
from bot.handlers.ask import ask_handler
from bot.handlers.check_link import check_link_handler
from bot.handlers.services import services
from bot.handlers.feedback import feedback_handler

# Load environment variables
load_dotenv()

# Try to connect to the database
db = get_db_connection()
if not db:
    print("Failed to connect to the database. Please check your database settings in .env file.")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Извините, произошла ошибка. Пожалуйста, попробуйте позже."
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

def main():
    # Initialize bot with your token
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", main_menu))
    app.add_handler(CommandHandler("services", services))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(feedback_handler)  # Add the new feedback conversation handler
    app.add_handler(ask_handler)
    app.add_handler(check_link_handler)

    initialize_database() # для создания таблиц при включении бота
    # Add error handler
    app.add_error_handler(error_handler)

    # Start the bot
    print("Bot started...")
    app.run_polling()


