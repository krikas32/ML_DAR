import os
from openai import OpenAI
from dotenv import load_dotenv

class OpenAIService:
    def __init__(self):
        load_dotenv()
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError('OPENAI_API_KEY nie je nastavený v .env súbore')
        
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    async def validate_question_selection(self, selected_question, previous_answers):
        try:
            # Najprv otestujeme API kľúč
            await self.test_api_key()
            
            prompt = self.create_validation_prompt(selected_question, previous_answers)
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Si expert na výber otázok pre darčekový poradca. Tvoja úloha je validovať, či je vybraná otázka relevantná a užitočná pre získanie informácií o preferenciách pre darček."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=150
            )

            validation = response.choices[0].message.content
            return self.parse_validation_response(validation)
        except Exception as e:
            print(f'Chyba pri validácii otázky s OpenAI: {str(e)}')
            return False

    async def test_api_key(self):
        try:
            await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            print('OpenAI API kľúč je platný')
            return True
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 401:
                raise ValueError('Neplatný OpenAI API kľúč')
            raise

    def create_validation_prompt(self, selected_question, previous_answers):
        return f"""
        Predchádzajúce odpovede: {previous_answers}
        Vybraná otázka: {selected_question}
        
        Je táto otázka relevantná a užitočná pre získanie informácií o preferenciách pre darček?
        Odpovedz len "ÁNO" alebo "NIE".
        """

    def parse_validation_response(self, response):
        return response.strip().upper() == 'ÁNO' 