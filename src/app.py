import os
import asyncio
from dotenv import load_dotenv
from src.models.question_model import QuestionModel
from src.services.openai_service import OpenAIService
from src.data.questions import questions, QuestionType

async def get_user_answer(question):
    print(f"\n{question['text']}")
    
    if question['type'] == QuestionType.YES_NO:
        while True:
            answer = input("Odpoveď (áno/nie): ").lower()
            if answer in ['áno', 'nie']:
                return {'type': QuestionType.YES_NO, 'value': answer == 'áno'}
            print("Prosím odpovedzte 'áno' alebo 'nie'")
            
    elif question['type'] == QuestionType.SLIDER:
        while True:
            try:
                value = float(input(f"Zadajte hodnotu ({question['options']['min']}-{question['options']['max']}): "))
                if question['options']['min'] <= value <= question['options']['max']:
                    return {'type': QuestionType.SLIDER, 'value': value, 'max': question['options']['max']}
                print(f"Prosím zadajte hodnotu medzi {question['options']['min']} a {question['options']['max']}")
            except ValueError:
                print("Prosím zadajte platné číslo")
                
    elif question['type'] == QuestionType.MULTIPLE_CHOICE:
        print("Možnosti:")
        for i, option in enumerate(question['options']):
            print(f"{i+1}. {option}")
        while True:
            try:
                choice = int(input("Vyberte možnosť (číslo): "))
                if 1 <= choice <= len(question['options']):
                    return {'type': QuestionType.MULTIPLE_CHOICE, 'selected_index': choice-1, 'options': question['options']}
                print(f"Prosím vyberte číslo medzi 1 a {len(question['options'])}")
            except ValueError:
                print("Prosím zadajte platné číslo")

async def main():
    # Načítame premenné prostredia
    load_dotenv()
    
    # Inicializujeme služby
    model = QuestionModel()
    openai_service = OpenAIService()
    
    # Načítame model
    await model.load_model()
    
    # Inicializujeme OpenAI službu
    if not openai_service.test_api_key():
        print('Chyba: OpenAI API kľúč nie je platný')
        return
    
    print('Systém odporúčania darčekov je pripravený!')
    
    # Inicializujeme premenné pre sledovanie odpovedí
    previous_answers = []
    available_questions = questions.copy()
    
    # Hlavná slučka pre otázky
    while len(previous_answers) < 20 and available_questions:
        # Vyberieme ďalšiu otázku
        selected_question = await model.select_next_question(previous_answers, available_questions)
        
        # Získame odpoveď od používateľa
        answer = await get_user_answer(selected_question)
        
        # Pridáme odpoveď do histórie
        previous_answers.append(answer)
        
        # Odstránime použitú otázku z dostupných
        available_questions = [q for q in available_questions if q['id'] != selected_question['id']]
        
        # Validujeme výber otázky pomocou OpenAI
        is_valid = openai_service.validate_question_selection(selected_question, previous_answers)
        if not is_valid:
            print("Táto otázka nie je relevantná, skúsim inú...")
            continue
            
        print(f"Vaša odpoveď: {answer}")
        
    print("\nĎakujeme za vaše odpovede! Na základe vašich odpovedí môžeme odporučiť vhodný darček.")

if __name__ == '__main__':
    asyncio.run(main()) 