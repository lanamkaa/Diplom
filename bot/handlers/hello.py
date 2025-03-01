from telegram.ext import ConversationHandler
from .main_menu import main_menu
from .services import services
from .ask import ASK_RESPONSE

async def hello_button(update, context):
    """Handle button presses in the main menu."""
    try:
        query = update.callback_query
        await query.answer()  # Answer the callback query to remove the loading state

        if query.data == "main_menu":
            return await main_menu(update, context)
        elif query.data == "show_services":
            return await services(update, context)
        elif query.data == "ask_response":
            await query.edit_message_text("Какой у вас вопрос?")
            return ASK_RESPONSE
        else:
            await query.edit_message_text("Пока в процессе")
            return ConversationHandler.END
    except Exception as e:
        print(f"Error in hello_button: {e}")
        return ConversationHandler.END
