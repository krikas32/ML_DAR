import os
from openai import OpenAI
from dotenv import load_dotenv

class OpenAIService:
    def __init__(self):
        load_dotenv()
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError('OPENAI_API_KEY nie je nastavený v .env súbore')
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def test_api_key(self):
        try:
            self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}]
            )
            print('OpenAI API kľúč je platný')
            return True
        except Exception as e:
            print(f'Chyba pri testovaní OpenAI API kľúča: {str(e)}')
            return False

    def validate_question_selection(self, selected_question, previous_answers):
        try:
            # Vytvoríme prompt pre validáciu
            prompt = self.create_validation_prompt(selected_question, previous_answers)
            
            # Získame odpoveď od OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Spracujeme odpoveď
            return self.parse_validation_response(response.choices[0].message.content)
        except Exception as e:
            print(f'Chyba pri validácii otázky: {str(e)}')
            return False

    def create_validation_prompt(self, selected_question, previous_answers):
        prompt = f"Validuj, či je nasledujúca otázka relevantná na základe predchádzajúcich odpovedí:\n\n"
        prompt += f"Predchádzajúce odpovede:\n"
        for i, answer in enumerate(previous_answers, 1):
            prompt += f"{i}. {answer}\n"
        prompt += f"\nVybraná otázka: {selected_question['text']}\n"
        prompt += "\nOdpovedz len 'áno' alebo 'nie'."
        return prompt

    def parse_validation_response(self, response):
        response = response.lower().strip()
        return response in ['áno', 'yes', 'true', '1'] 