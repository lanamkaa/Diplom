import json
import requests
import re

msg = "Ты консультант по вопросам цифровых сервисов НГТУ.\n" \
      "Спросили про цифровые сервисы ищи информацию тут: https://kb.nstu.ru/it:services.\n" \
      "Про единую учетную запись: https://kb.nstu.ru/it:id\n" \
      "Про корпоративную почтовую систему: https://kb.nstu.ru/it:mail:start\n" \
      "Про личный кабинет тут: https://kb.nstu.ru/it:lk\n" \
      "Про Dispase: https://dispace.edu.nstu.ru\n" \
      "Про информационную систему: https://kb.nstu.ru/it:is:remoteapp\n" \
      "Про облачную платформу: https://cloud.nstu.ru/wiki/\n" \
      "Облачное файловое хранилище: https://kb.nstu.ru/it:store\n" \
      "Система электронного документа оборота: https://kb.nstu.ru/tezis:tezis\n" \
      "Система 1с: https://kb.nstu.ru/it:1c\n" \
      "Беспроводная сеть WI-FI: https://kb.nstu.ru/it:wifi\n" \
      "ВСЕГДА отвечай в формате JSON с такой структурой: {\"question_type\": string, \"answer\": string} \n" \
      "question_type должен быть одним из: 'services', 'id', 'mail', 'lk', 'dispace', 'is', 'cloud', 'storage', 'docflow', '1c', 'wifi'\n" \
      "Если вопрос не относится к конкретному сервису, используй 'general'"

prefix = "Сразу отвечай на вопрос пользователя в формате JSON."

async def yandex_gpt_query(user_ask):
    prompt = {
        "modelUri": "gpt://b1gnnevplbv23go5bath/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.2,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": msg + prefix
            },
            {
                "role": "user",
                "text": user_ask
            }
        ]
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key AQVN3wCQ2XiptIikPYbaCM-cPFoJ4rk8gZBpEUJX"
    }
    response = requests.post(url, headers=headers, json=prompt)
    result = response.json()

    text_response = result['result']['alternatives'][0]['message']['text']
    
    # Remove markdown code block formatting
    text_response = re.sub(r'```json\n?|\n?```', '', text_response)
    text_response = text_response.strip()
    # Ensure the response is valid JSON
    try:
        json_response = json.loads(text_response)
        if not isinstance(json_response, list):
            json_response = [json_response]
    except json.JSONDecodeError:
        json_response = [{"question_type": "general", "answer": text_response}]

    return json_response[0]['answer'], json_response[0]['question_type']