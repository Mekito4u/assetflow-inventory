from gigachat import GigaChat
from django.conf import settings
from .prompts import REQUEST_ANALYSIS_PROMPT
import json
import re


class GigaChatService:
    """Сервис для анализа заявок через GigaChat API"""

    def __init__(self):
        """Инициализация сервиса с настройками аутентификации"""
        self.credentials = settings.GIGACHAT_API_KEY
        self.system_prompt = REQUEST_ANALYSIS_PROMPT

    def analyze_request(self, employee_position, device_type, purpose):
        """
        Анализирует заявку на оборудование через GigaChat

        Args:
            employee_position: Должность сотрудника
            device_type: Тип оборудования
            purpose: Цель использования

        Returns:
            dict: Результат анализа с полями priority_score, tags, summary, needs_clarification
        """
        try:
            with GigaChat(credentials=self.credentials, verify_ssl_certs=False) as giga:

                user_message = f"""
СОТРУДНИК: {employee_position}
ОБОРУДОВАНИЕ: {device_type} 
ЦЕЛЬ: {purpose}
"""

                full_prompt = f"{self.system_prompt}\n\n{user_message}"

                response = giga.chat(full_prompt)
                ai_response = response.choices[0].message.content

                cleaned_response = re.sub(r'^```json|```$', '', ai_response).strip()
                analysis_result = json.loads(cleaned_response)

                return analysis_result

        except Exception as e:
            return {
                "priority_score": 5,
                "tags": ["ошибка анализа"],
                "summary": "Не удалось проанализировать заявку",
                "needs_clarification": True,
                "clarification_questions": ["Опишите подробнее вашу задачу"]
            }