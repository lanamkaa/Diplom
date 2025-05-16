from typing import Dict, Any, Tuple
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

async def yandex_gpt_request(prompt: str) -> Dict[str, Any]:
    """
    Отправляет запрос к YandexGPT и получает ответ.
    
    Args:
        prompt: Промпт для генерации ответа
        
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
            {
                "role": "system",
                "text": system_prompt
            },
            {
                "role": "user",
                "text": prompt
            }
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

async def identify_question_type(question: str) -> Tuple[str, float, bool]:
    """
    Первый шаг: определение типа вопроса.
    
    Args:
        question: Вопрос пользователя
        
    Returns:
        Tuple[str, float, bool]: (тип вопроса, уверенность, валидность)
    """
    services_list = "\n".join([f"- {service['name']}" for service in SERVICES_CONFIG.values()])
    prompt = QUESTION_TYPE_PROMPT.format(services_list=services_list)
    
    # Добавляем вопрос пользователя в промпт
    full_prompt = f"{prompt}\n\nВопрос пользователя: {question}"
    
    try:
        response = await yandex_gpt_request(full_prompt)
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

async def generate_answer(question: str, question_type: str) -> Tuple[str, str]:
    """
    Второй шаг: генерация ответа на основе типа вопроса.
    
    Args:
        question: Вопрос пользователя
        question_type: Определенный тип вопроса
        
    Returns:
        Tuple[str, str]: (ответ, дополнительная информация)
    """
    if question_type not in SERVICES_CONFIG:
        return "Извините, я не могу найти информацию по этому вопросу.", ""
    
    service = SERVICES_CONFIG[question_type]
    
    # Получаем контент с URL сервиса
    scraped_content = scrape_url(service['url'])
    if not scraped_content:
        logger.warning(f"Не удалось получить контент с URL: {service['url']}")
        content_text = "Информация недоступна"
    else:
        content_text = scraped_content['text']
        
    print('content_text', content_text)
    prompt = ANSWER_PROMPT.format(
        service_name=service['name'],
        service_description=service['description'],
        service_url=service['url'],
        service_content=content_text
    )
    
    # Добавляем вопрос пользователя в промпт
    full_prompt = f"{prompt}\n\nВопрос пользователя: {question}"
    
    try:
        response = await yandex_gpt_request(full_prompt)
        if "error" in response:
            return "Произошла ошибка при генерации ответа.", ""
            
        return (
            response.get("answer", "Извините, не удалось сгенерировать ответ."),
            response.get("additional_info", "")
        )
    except Exception as e:
        logger.error(f"Ошибка при генерации ответа: {e}")
        return "Произошла ошибка при генерации ответа.", ""

async def yandex_gpt_query(user_question: str) -> Tuple[str, str, bool]:
    """
    Основная функция для обработки запроса пользователя.
    Выполняет двухшаговый процесс: определение типа вопроса и генерация ответа.
    
    Args:
        user_question: Вопрос пользователя
        
    Returns:
        Tuple[str, str, bool]: (ответ, тип вопроса, валидность вопроса)
    """
    # Шаг 1: Определение типа вопроса
    question_type, confidence, is_valid = await identify_question_type(user_question)
    logger.info('Question type identification: type=%s, confidence=%f, valid=%s', 
                question_type, confidence, is_valid)
    print('Шаг 1')
    print(confidence)
    if not is_valid or confidence < 0.5:
        return "Извините, я не могу определить, к какому сервису относится ваш вопрос.", "general", False

    # Шаг 2: Генерация ответа
    answer, additional_info = await generate_answer(user_question, question_type)
    logger.info('Answer generation: answer=%s, additional_info=%s', answer, additional_info)
    
    # Формируем полный ответ
    full_answer = answer
    if additional_info:
        full_answer += f"\n\nДополнительная информация:\n{additional_info}"
    
    return full_answer, question_type, True