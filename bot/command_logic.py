valid_commands = ["start", "services", "ask", "help", "feedback", "check_link", "analyze"]

keyword_groups = {
    'start': ['начать', 'старт', 'запуск', 'давай начнем', 'поехали', 'start', 'go', 'begin'],
    'services': ['услуги', 'сервисы', 'service', 'показать сервисы', 'доступные услуги', 'какие есть сервисы', 'services', 'tools'],
    'ask': ['вопрос', 'спросить', 'ask', 'задать вопрос', 'задать гпт', 'у меня вопрос', 'question', 'ask a question'],
    'help': ['помощь', 'справка', 'help', 'что ты умеешь', 'как пользоваться', 'поддержка', 'assist', 'support', 'guide'],
    'feedback': ['отзыв', 'фидбек', 'feedback', 'оставить отзыв', 'написать отзыв', 'мнение', 'review', 'comment'],
    'check_link': ['ссылка', 'проверить', 'link', 'проверка ссылки', 'ссылка безопасна', 'проверить ссылку', 'check link', 'is link safe', 'verify url'],
    'analyze': ['анализ', 'статистика', 'analyze', 'статистика вопросов', 'анализ вопросов', 'отчет', 'report', 'statistics']
}

layout_map = str.maketrans(
    "qwertyuiop[]asdfghjkl;'zxcvbnm,./",
    "йцукенгшщзхъфывапролджэячсмитьбю."
)
reverse_layout_map = str.maketrans(
    "йцукенгшщзхъфывапролджэячсмитьбю.",
    "qwertyuiop[]asdfghjkl;'zxcvbnm,./"
)

def normalize(text):
    return text.strip().lower()

def fix_layout_ru_to_en(text):
    return text.translate(reverse_layout_map)

def fix_layout_en_to_ru(text):
    return text.translate(layout_map)

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2): return levenshtein_distance(s2, s1)
    if not s2: return len(s1)
    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insert = prev_row[j + 1] + 1
            delete = curr_row[j] + 1
            replace = prev_row[j] + (c1 != c2)
            curr_row.append(min(insert, delete, replace))
        prev_row = curr_row
    return prev_row[-1]

def find_closest_command(user_input):
    min_distance = float("inf")
    closest = None
    for cmd in valid_commands:
        dist = levenshtein_distance(user_input, cmd)
        if dist <= 2 and dist < min_distance:
            min_distance = dist
            closest = cmd
    return closest

def handle_command_input(user_input):
    user_input = normalize(user_input)
    is_command = user_input.startswith("/")
    text = user_input[1:] if is_command else user_input

    # 1. Попытка исправить раскладку
    for fix_func in [fix_layout_ru_to_en, fix_layout_en_to_ru]:
        fixed = fix_func(text)
        if fixed in valid_commands:
            return f"💡 Возможно, вы имели в виду /{fixed}?"

    # 2. Поиск по ключевым словам
    for cmd, keywords in keyword_groups.items():
        for keyword in keywords:
            if keyword in text:
                return f"💡 Похоже, вы имели в виду /{cmd}"

    # 3. Поиск по Левенштейну
    closest_cmd = find_closest_command(text)
    if closest_cmd:
        if is_command:
            return f"⚠️ Неизвестная команда. Возможно, вы имели в виду /{closest_cmd}?"
        else:
            return f"🤔 Вы написали '{user_input}'. Возможно, вы имели в виду /{closest_cmd}?"

    # Ничего не найдено
    return "🤷 Команда не найдена.\n Доступные команды:\n" + "\n".join(f"/{cmd}" for cmd in valid_commands)
