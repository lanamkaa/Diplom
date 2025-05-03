from ..database.users.get_inactive_users import get_inactive_users
from ..database.users.get_user import get_user_by_telegram_id
from ..database.users.update_reminder_sent import update_reminder_sent_at

async def send_reminders(context):
    """
    Отправляет напоминания пользователям, которые были неактивны более 7 дней.
    """
    inactive_users = get_inactive_users(days=7)
    print(f"📢 Найдено {len(inactive_users)} неактивных пользователей.")

    for telegram_id in inactive_users:
        try:
            user = get_user_by_telegram_id(telegram_id)

            if not user:
                print(f"⚠️ Пользователь с telegram_id={telegram_id} не найден в базе.")
                continue

            # user = (user_id, username, first_name, created_at, last_active_at)
            first_name = user[2] or "друг"

            message = (
                f"👋 Привет, {first_name}!\n"
                "Давно не виделись 😊\n\n"
                "Я всё ещё здесь, если нужно:\n"
                "— найти сервис\n"
                "— задать вопрос\n"
                "— проверить ссылку\n\n"
                "Напиши /help — и я напомню, что умею!"
            )

            await context.bot.send_message(chat_id=telegram_id, text=message)
            update_reminder_sent_at(telegram_id)

            print(f"✅ Напоминание успешно отправлено {telegram_id}")

        except Exception as e:
            print(f"❌ Ошибка при отправке напоминания пользователю {telegram_id}: {e}")
