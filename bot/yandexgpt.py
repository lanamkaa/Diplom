from typing import Dict, Any, Tuple, List
import requests
from dotenv import load_dotenv
import logging
import json
from bot.scraper import scrape_url

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация сервисов НГТУ
SERVICES_CONFIG = {
    'services': {
        'name': 'Цифровые сервисы',
        'url': 'https://kb.nstu.ru/it:services',
        'description': 'Общая информация о цифровых сервисах'
    },
    'id': {
        'name': 'Единая учетная запись',
        'url': 'https://kb.nstu.ru/it:id',
        'description': 'Информация о единой учетной записи'
    },
    'mail': {
        'name': 'Корпоративная почтовая система',
        'url': 'https://kb.nstu.ru/it:mail:start',
        'description': 'Работа с корпоративной почтой'
    },
    'lk': {
        'name': 'Личный кабинет',
        'url': 'https://kb.nstu.ru/it:lk',
        'description': 'Информация о личном кабинете'
    },
    'dispace': {
        'name': 'Dispase',
        'url': 'https://dispace.edu.nstu.ru',
        'description': 'Образовательная платформа'
    },
    'is': {
        'name': 'Информационная система',
        'url': 'https://kb.nstu.ru/it:is:remoteapp',
        'description': 'Удаленный доступ к информационной системе'
    },
    'cloud': {
        'name': 'Облачная платформа',
        'url': 'https://cloud.nstu.ru/wiki/',
        'description': 'Облачные сервисы НГТУ'
    },
    'storage': {
        'name': 'Облачное файловое хранилище',
        'url': 'https://kb.nstu.ru/it:store',
        'description': 'Хранение файлов в облаке'
    },
    'docflow': {
        'name': 'Система электронного документооборота',
        'url': 'https://kb.nstu.ru/tezis:tezis',
        'description': 'Работа с электронными документами'
    },
    '1c': {
        'name': 'Система 1С',
        'url': 'https://kb.nstu.ru/it:1c',
        'description': 'Работа с системой 1С'
    },
    'wifi': {
        'name': 'Беспроводная сеть WI-FI',
        'url': 'https://kb.nstu.ru/it:wifi',
        'description': 'Подключение к Wi-Fi сети'
    },
    'general': {
        'name': 'Общий вопрос про сервисы НГТУ',
        'url': 'https://kb.nstu.ru/it:services',
        'description': 'Нужно ответить на вопрос пользователя, в контексте сервисов НГТУ, и разбить по пунктам'
    }
}

# Базовый промпт для GPT
BASE_PROMPT = "Ты консультант по вопросам цифровых сервисов НГТУ."

# Промпт для определения типа вопроса
QUESTION_TYPE_PROMPT = """
Определи тип вопроса пользователя. Вопрос должен относиться к одному из следующих сервисов НГТУ:
{services_list}

Ответь в формате JSON:
{{
    "question_type": "string",  // один из типов сервисов или 'general'
    "confidence": float,        // уверенность в определении типа (0-1)
    "valid_question": boolean   // является ли вопрос валидным
}}
"""

# Промпт для генерации ответа
ANSWER_PROMPT = """
Сгенерируй ответ на вопрос пользователя, используя информацию о сервисе:
Название сервиса: {service_name}
Описание: {service_description}
URL: {service_url}

Содержимое страницы сервиса:
{service_content}

Ответь в формате JSON:
{{
    "answer": "string",
    "additional_info": "string"  // дополнительная полезная информация
}}
"""

system_prompt = "Ты консультант по вопросам цифровых сервисов НГТУ."

async def yandex_gpt_request(messages: List[Dict[str, Any]], system_message: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Отправляет запрос к YandexGPT и получает ответ.
    
    Args:
        messages: Список сообщений для запроса
        
    Returns:
        Dict[str, Any]: Распарсенный JSON ответ
    """
    body = {
        "modelUri": "gpt://b1gnnevplbv23go5bath/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.2,
            "maxTokens": "2000"
        },
        "messages": [
            system_message,
            *messages
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key AQVN3wCQ2XiptIikPYbaCM-cPFoJ4rk8gZBpEUJX"
    }
    response = requests.post(url, headers=headers, json=body)
    result = response.json()

    text_response = result['result']['alternatives'][0]['message']['text']
    logger.info('Raw response: %s', text_response)
    
    try:
        # Remove any markdown code block formatting
        text_response = text_response.replace('```json', '').replace('```', '').strip()
        return json.loads(text_response)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON response: {e}")
        return {"error": "Failed to parse response"}

def get_service_key_by_name(service_name: str) -> str:
    """
    Получает ключ сервиса по его названию.
    
    Args:
        service_name: Название сервиса
        
    Returns:
        str: Ключ сервиса или 'general' если не найден
    """
    for key, service in SERVICES_CONFIG.items():
        if service['name'].lower() == service_name.lower():
            return key
    return "general"

async def identify_question_type(question: str, messages_history: List[Dict[str, Any]] = None) -> Tuple[str, float, bool]:
    """
    Первый шаг: определение типа вопроса.
    
    Args:
        question: Вопрос пользователя
        messages_history: История сообщений для контекста
        
    Returns:
        Tuple[str, float, bool]: (тип вопроса, уверенность, валидность)
    """
    services_list = "\n".join([f"- {service['name']}" for service in SERVICES_CONFIG.values()])
    prompt = QUESTION_TYPE_PROMPT.format(services_list=services_list)
    
    # Формируем сообщения для запроса
    messages = []
    formatting_hints = "answer должен быть отформатирован в виде списка, ссылок, таблиц, и т.д."


    system_message = {
        "role": "system",
        "text":  f"{prompt}\n\n {system_prompt}\n\n {formatting_hints}"
    }
    
    # Добавляем историю сообщений, если она есть
    if messages_history:
        messages.extend(messages_history)
    
    # Добавляем текущий вопрос
    messages.append({
        "role": "user",
        "text": question
    })
    
    logger.info('Messages for question type identification: %s', messages)

    try:
        response = await yandex_gpt_request(messages, system_message)
        if "error" in response:
            return "general", 0.0, False
            
        # Получаем название сервиса из ответа
        service_name = response.get("question_type", "general")
        # Преобразуем название в ключ сервиса
        service_key = get_service_key_by_name(service_name)
            
        return (
            service_key,
            float(response.get("confidence", 0.0)),
            bool(response.get("valid_question", False))
        )
    except Exception as e:
        logger.error(f"Ошибка при определении типа вопроса: {e}")
        return "general", 0.0, False

async def generate_answer(question: str, question_type: str, messages_history: list = None) -> str:
    """
    Генерирует ответ на вопрос с учетом типа вопроса и истории сообщений.
    
    Args:
        question: Текст вопроса
        question_type: Тип вопроса (ключ из SERVICES_CONFIG)
        messages_history: История сообщений для контекста
        
    Returns:
        str: Сгенерированный ответ
    """
    try:
        if question_type not in SERVICES_CONFIG:
            return "Извините, я не могу найти информацию по этому сервису."

        service = SERVICES_CONFIG[question_type]
        
        # Получаем контент с сайта сервиса
        content = scrape_url(service['url'])
        content_text = content.get('text', 'Информация недоступна') if content else 'Информация недоступна'
        
        # Формируем промпт с учетом истории
        system_prompt = ANSWER_PROMPT.format(
            service_name=service['name'],
            service_description=service['description'],
            service_url=service['url'],
            service_content=content_text
        )
        
        # Формируем сообщения для запроса
        messages = []

        system_message = {
            "role": "system",
            "text": system_prompt
        }
        
        # Добавляем историю сообщений, если она есть
        if messages_history:
            messages.extend(messages_history)
            
        # Добавляем текущий вопрос
        messages.append({
            "role": "user",
            "text": question
        })
      
        # Отправляем запрос к YandexGPT
        response = await yandex_gpt_request(messages, system_message)
        
        if not response:
            return "Извините, не удалось получить ответ. Пожалуйста, попробуйте позже."
            
        # Проверяем, является ли ответ уже словарем
        if isinstance(response, dict):
            return response.get('answer', 'Не удалось сформировать ответ.')
            
        # Если ответ - строка, пытаемся распарсить JSON
        try:
            answer_data = json.loads(response)
            return answer_data.get('answer', 'Не удалось сформировать ответ.')
        except json.JSONDecodeError:
            # Если не удалось распарсить JSON, возвращаем ответ как есть
            return response
            
    except Exception as e:
        logger.error(f"Ошибка при генерации ответа: {str(e)}")
        return "Произошла ошибка при генерации ответа."

async def yandex_gpt_query(msg: str, messages_history: list = None) -> Tuple[str, str, bool]:
    """
    Отправляет запрос к YandexGPT и возвращает ответ.
    
    Args:
        msg: Текст запроса
        messages_history: История сообщений для контекста
        
    Returns:
        Tuple[str, str, bool]: (ответ, тип вопроса, валидность вопроса)
    """
    try:
        # Определяем тип вопроса
        question_type, confidence, valid_question = await identify_question_type(msg, messages_history)
        
        if not valid_question:
            return "Извините, я не могу определить, к какому сервису относится ваш вопрос. Пожалуйста, уточните вопрос.", "general", False
            
        if confidence < 0.7:
            return "Извините, я не уверен, что правильно понял ваш вопрос. Пожалуйста, переформулируйте его.", "general", False
            
        # Получаем ответ
        answer = await generate_answer(msg, question_type, messages_history)
        return answer, question_type, True
        
    except Exception as e:
        logger.error(f"Ошибка при генерации ответа: {str(e)}")
        return "Произошла ошибка при генерации ответа.", "general", False