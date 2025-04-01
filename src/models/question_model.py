import tensorflow as tf
import numpy as np
import os
from pathlib import Path
from ..data.questions import QuestionType
from ..services.dropbox_service import DropboxService

class QuestionModel:
    def __init__(self):
        self.model = None
        self.consecutive_successes = 0
        self.required_successes = 3
        self.model_path = Path(os.getenv('MODEL_SAVE_PATH', './models')) / 'question_model'
        self.dropbox = DropboxService()

    def build_model(self):
        print('Vytváram nový model...')
        # Overíme GPU dostupnosť
        gpu_devices = tf.config.list_physical_devices('GPU')
        if gpu_devices:
            print(f'Používam GPU: {gpu_devices[0].name}')
        else:
            print('GPU nie je dostupná, používam CPU')

        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(150,)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(20, activation='softmax')
        ])

        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        print('Model bol úspešne vytvorený')

    async def select_next_question(self, previous_answers, available_questions):
        if self.model is None:
            self.build_model()

        # Konvertujeme predchádzajúce odpovede na tensor
        input_tensor = self.preprocess_answers(previous_answers)
        
        # Predikujeme ďalšiu otázku
        prediction = self.model.predict(input_tensor, verbose=0)
        
        # Vyberieme otázku s najvyššou pravdepodobnosťou z dostupných otázok
        available_indices = [q['id'] - 1 for q in available_questions]
        prediction[0, [i for i in range(20) if i not in available_indices]] = -float('inf')
        selected_question_index = np.argmax(prediction[0])
        
        # Nájdeme otázku podľa indexu
        for question in available_questions:
            if question['id'] - 1 == selected_question_index:
                return question
                
        # Ak sa niečo pokazí, vrátime prvú dostupnú otázku
        return available_questions[0]

    def preprocess_answers(self, answers):
        # Konvertujeme odpovede na vektor
        vector = np.zeros(150)
        for i, answer in enumerate(answers):
            vector[i] = self.normalize_answer(answer)
        return np.array([vector])

    def normalize_answer(self, answer):
        if answer['type'] == QuestionType.YES_NO:
            return 1 if answer['value'] else 0
        elif answer['type'] == QuestionType.SLIDER:
            return answer['value'] / answer['max']
        elif answer['type'] == QuestionType.MULTIPLE_CHOICE:
            return answer['selected_index'] / len(answer['options'])
        return 0

    async def save_model(self):
        if self.model is None:
            raise ValueError('Model nie je inicializovaný')

        try:
            # Vytvoríme priečinok ak neexistuje
            self.model_path.parent.mkdir(parents=True, exist_ok=True)

            # Uložíme model lokálne
            self.model.save(self.model_path)
            
            # Overíme či sa súbory skutočne vytvorili
            model_files = ['model.json', 'weights.bin']
            all_files_exist = all(
                (self.model_path / file).exists() for file in model_files
            )

            if not all_files_exist:
                raise ValueError('Niektoré súbory modelu sa neuložili správne')

            # Nahrajeme model na Dropbox
            await self.dropbox.initialize()
            uploaded = await self.dropbox.upload_model(str(self.model_path))

            if not uploaded:
                raise ValueError('Chyba pri nahrávaní modelu na Dropbox')

            print('Model bol úspešne uložený lokálne a na Dropbox')
            return True
        except Exception as e:
            print(f'Chyba pri ukladaní modelu: {str(e)}')
            return False

    async def load_model(self):
        try:
            # Skúsime načítať model z Dropboxu
            await self.dropbox.initialize()
            downloaded = await self.dropbox.download_model(str(self.model_path))

            if not downloaded:
                print('Žiadny model nebol nájdený na Dropboxe, vytváram nový...')
                self.build_model()
                return False

            print('Načítavam model z Dropboxu...')
            self.model = tf.keras.models.load_model(self.model_path)
            print('Model bol úspešne načítaný')
            return True
        except Exception as e:
            print(f'Chyba pri načítaní modelu: {str(e)}')
            print('Vytváram nový model...')
            self.build_model()
            return False 