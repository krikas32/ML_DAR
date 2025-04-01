import os
import asyncio
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv
from src.models.question_model import QuestionModel
from src.services.openai_service import OpenAIService
from src.data.questions import questions

async def generate_training_data(num_samples=1000):
    # Generujeme náhodné tréningové dáta
    X = np.random.rand(num_samples, 150)  # 150 otázok
    y = np.random.randint(0, 20, num_samples)  # 20 možných otázok
    return X, y

async def main():
    # Načítame premenné prostredia
    load_dotenv()
    
    # Inicializujeme služby
    model = QuestionModel()
    openai_service = OpenAIService()
    
    # Skúsime načítať existujúci model
    await model.load_model()
    
    # Testujeme OpenAI API
    if not openai_service.test_api_key():
        print('Chyba: OpenAI API kľúč nie je platný')
        return
    
    print('Začínam trénovanie modelu...')
    
    # Generujeme tréningové dáta
    X_train, y_train = await generate_training_data()
    
    # Trénujeme model
    history = model.model.fit(
        X_train,
        tf.keras.utils.to_categorical(y_train, num_classes=20),
        epochs=50,
        batch_size=32,
        validation_split=0.2
    )
    
    # Uložíme model
    await model.save_model()
    
    print('Trénovanie dokončené')
    print(f'Finálna presnosť: {history.history["accuracy"][-1]:.2f}')

if __name__ == '__main__':
    asyncio.run(main()) 