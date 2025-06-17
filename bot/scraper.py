import requests
from bs4 import BeautifulSoup
import logging
from typing import Optional, Dict
from urllib.parse import urlparse
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Очищает текст от лишних пробелов и переносов строк, сохраняя значимые переносы.
    
    Args:
        text: Исходный текст
        
    Returns:
        str: Очищенный текст с сохраненными значимыми переносами строк
    """
    # Разбиваем текст на строки
    lines = text.split('\n')
    
    # Очищаем каждую строку
    cleaned_lines = []
    for line in lines:
        # Удаляем множественные пробелы в строке
        line = re.sub(r'\s+', ' ', line)
        # Удаляем пробелы в начале и конце строки
        line = line.strip()
        # Добавляем непустые строки
        if line:
            cleaned_lines.append(line)
    
    # Объединяем строки, сохраняя переносы
    return '\n'.join(cleaned_lines)

def format_list_items(text: str) -> str:
    """
    Форматирует элементы списка для лучшей читаемости.
    
    Args:
        text: Исходный текст
        
    Returns:
        str: Отформатированный текст
    """
    # Добавляем перенос строки перед элементами списка
    text = re.sub(r'(\d+[\.\)]|\-|\*)\s+', r'\n\1 ', text)
    # Добавляем перенос строки перед двоеточием
    text = re.sub(r':\s+', ':\n', text)
    return text

def scrape_url(url: str) -> Optional[Dict[str, str]]:
    """
    Скрапит текст с указанного URL.
    
    Args:
        url: URL для скрапинга
        
    Returns:
        Optional[Dict[str, str]]: Словарь с заголовком и текстом страницы или None в случае ошибки
    """
    try:
        # Проверяем URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            logger.error(f"Invalid URL: {url}")
            return None

        # Отправляем запрос
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Проверяем на ошибки HTTP

        # Парсим HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Получаем заголовок
        title = soup.title.string if soup.title else "Нет заголовка"
        title = clean_text(title)

        # Удаляем ненужные элементы
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Получаем основной текст
        text = soup.get_text()
        
        # Очищаем и форматируем текст
        text = clean_text(text)
        text = format_list_items(text)

        # Если текст слишком короткий, возможно, это не HTML страница
        if len(text) < 100:
            logger.warning(f"Контент слишком короткий: {url}")
            return None

        return {
            'title': title,
            'text': text,
            'url': url
        }

    except requests.RequestException as e:
        logger.error(f"Ошибка получения страницы {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при скрапинге {url}: {e}")
        return None

def get_main_content(url: str) -> Optional[str]:
    """
    Получает основной контент страницы, пытаясь найти наиболее релевантный текст.
    
    Args:
        url: URL для скрапинга
        
    Returns:
        Optional[str]: Основной контент страницы или None в случае ошибки
    """
    try:
        result = scrape_url(url)
        if not result:
            return None

        # Если текст слишком длинный, пытаемся найти основной контент
        if len(result['text']) > 5000:
            # Ищем тег main или article
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            main_content = soup.find('main') or soup.find('article')
            
            if main_content:
                text = clean_text(main_content.get_text())
                if len(text) > 100:  # Проверяем, что нашли достаточно текста
                    return text

        return result['text']

    except Exception as e:
        logger.error(f"Ошибка при получении основного контента с {url}: {e}")
        return None 