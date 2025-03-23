import requests

msg = "Ты консультант по вопросам цифровых сервисов НГТУ./nИ ответь с такой структурой" \
       "Спросили про цифровые сервисы ищи информацию тут: https://kb.nstu.ru/it:services./n" \
       "Про единую учетную запись: https://kb.nstu.ru/it:id" \
       "Про корпоративную почтовую систему: https://kb.nstu.ru/it:mail:start" \
       "Про личный кабинет тут: https://kb.nstu.ru/it:lk" \
       "Про Dispase: https://dispace.edu.nstu.ru" \
       "Про информационную систему: https://kb.nstu.ru/it:is:remoteapp" \
       "Про облачную платформу: https://cloud.nstu.ru/wiki/" \
       "Облачное файловое хранилище: https://kb.nstu.ru/it:store" \
       "Система электронного документа оборота: https://kb.nstu.ru/tezis:tezis" \
       "Система 1с: https://kb.nstu.ru/it:1c" \
       "Беспроводная сеть WI-FI: https://kb.nstu.ru/it:wifi"
prefix = "Сразу отвечай на вопрос пользователя."
async def yandex_gpt_query(user_ask):
    prompt = {
        "modelUri": "gpt://b1gnnevplbv23go5bath/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
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
    return text_response