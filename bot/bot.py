from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram.error import TelegramError
import logging
from bot.database.connect import get_db_connection
from bot.database.users.update_new_user import update_user
from dotenv import load_dotenv
import os
import sys

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

# Import handlers
from bot.handlers.start import start
from bot.handlers.hello import hello_button
from bot.handlers.help import help
from bot.handlers.main_menu import main_menu
from bot.handlers.ask import ask_gpt, ask_handler, ASK_RESPONSE
from bot.handlers.feedback import cancel, feedback_handler
from bot.handlers.services import services

# Create conversation handler for hello functionality
hello_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(hello_button)],
    states={
        ASK_RESPONSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gpt)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=False
)

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
    app.add_handler(feedback_handler)
    app.add_handler(ask_handler)
    app.add_handler(hello_handler)
    app.add_handler(CallbackQueryHandler(hello_button))

    # Add error handler
    # app.add_error_handler(error_handler)

    # Start the bot
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
