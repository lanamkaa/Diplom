from typing import Optional, Tuple
from ..database.questions.create_question import create_question
from ..database.questions.update_question import update_question

def ask_gpt_workflow(user_id: int, question_text: str, gpt_response: str) -> Tuple[bool, Optional[int]]:
    """
    Создаёт вопрос в базе и сохраняет ответ от GPT.
    """
    question_id = create_question(user_id, question_text)
    if question_id is None:
        print("❌ Не удалось создать запись вопроса")
        return False, None
    
    update_success = update_question(question_id, {"answer_text": gpt_response})
    if not update_success:
        print(f"❌ Не удалось обновить вопрос {question_id} с помощью ответа GPT")
        return False, question_id
    
    print(f"✅ Успешно обработан ask_gpt для вопроса {question_id}")
    return True, question_id

def rate_answer(question_id: int, rating: int):
    """
    Сохраняет оценку (от 1 до 5 звёзд) для ответа GPT.
    """
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        print(f"⚠️Неверный рейтинг: {rating}. Рейтинг должен быть целым числом от 1 до 5.")
        return False
    
    update_success = update_question(question_id, {"answer_rating": rating})
    if not update_success:
        print(f"❌ Не удалось обновить вопрос {question_id} с рейтингом {rating}")
        return False
    
    print(f"✅ Успешно оценили вопрос {question_id} на {rating} звезд")
    return True 