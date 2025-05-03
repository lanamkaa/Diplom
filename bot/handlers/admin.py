from telegram import Update
from telegram.ext import ContextTypes
from bot.database.analytics import get_bot_stats, get_low_rated_questions
from matplotlib import pyplot as plt
import io

ADMIN_IDS = [888737841]

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет доступа к административной панели.")
        return

    stats = get_bot_stats()
    low_rated = get_low_rated_questions(limit=5)

    text = f"\U0001F4CA Общая статистика:\n" \
           f"— Всего пользователей: {stats['user_count']}\n" \
           f"— Вопросов задано: {stats['question_count']}\n" \
           f"— Средняя оценка: {stats['avg_rating']:.2f}\n" \
           f"— Удовлетворённых ответов: {stats['good_pct']}%\n\n"

    text += "\u26A0\uFE0F Проблемные вопросы:\n"
    for q in low_rated:
        text += f"— {q['text'][:50]}... — оценка: {q['rating']:.1f} ({q['count']} отзывов)\n"

    await update.message.reply_text(text)

    # Отправка графика средних оценок по дням (пример, если будут даты)
    if 'daily_ratings' in stats:
        dates = [r['date'] for r in stats['daily_ratings']]
        ratings = [r['avg'] for r in stats['daily_ratings']]

        fig, ax = plt.subplots()
        ax.plot(dates, ratings, marker='o')
        ax.set_title('Средняя оценка по дням')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Оценка')
        plt.xticks(rotation=45)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        await update.message.reply_photo(photo=buf, caption="График средней оценки")
        buf.close()
