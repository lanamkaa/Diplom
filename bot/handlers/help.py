from ..utils.util import *

async def help(update, context):
    await send_photo(update, context, "картинка2")
    text = load_message("help")
    await send_text(update, context, text)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "🌐 *Наши социальные сети:*\n\n"
            "— [ВКонтакте НГТУ](https://vk.com/nstu_vk)\n"
            "— [Телеграм НГТУ](https://t.me/nstu_neti)\n"
            "— [Одноклассники НГТУ](https://ok.ru/ngtuneti)\n"
            "— [Rutube НГТУ](https://rutube.ru/channel/24953858/)\n"
            "— [Яндекс.Дзен НГТУ](https://dzen.ru/nstu_neti)\n"
            "— [Сайт НГТУ](https://www.nstu.ru)"
        ),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )