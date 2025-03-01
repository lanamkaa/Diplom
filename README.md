# DiplomaTime

Features: 
    1. Вопросы сервиса НГТУ
        1.1. Подключение к Яндекс ГПТ
        1.2. Ответы на локальные вопросы ВУЗа (фильтр ответов)
        1.3. Перенаправка на другой бот
    2. Скрапинг веб-страницы (ССЫЛОЧКА)
        2.1. Меню списка сервисов 
    3. Обратная связь (? после каждого/ после всего диалога)
        3.1. Подключение к БД
        3.2. Стастистика
        3.3. Система оценок

## How to Run
source venv/Scripts/activate && python -m bot

1. **Upgrade Python (if necessary):**
    Ensure you have Python 3.7 or higher installed. You can download it from [python.org](https://www.python.org/downloads/).

2. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/DiplomaTime.git
    cd DiplomaTime
    ```

3. **Create a virtual environment and activate it:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4. **Create a `requirements.txt` file:**
    ```sh
    echo -e "requests\nlxml\npython-telegram-bot" > requirements.txt
    ```

5. **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

6. **Run the bot:**
    ```sh
    python bot.py
    ```

7. **Set up environment variables:**
    Ensure you have the necessary environment variables set up, such as the bot token.

8. **Interacting with the bot:**
    Start a conversation with your bot on Telegram using the `/start` command.

Сайт для отображения стастики