from enum import Enum

class QuestionType(Enum):
    YES_NO = 'yes_no'
    MULTIPLE_CHOICE = 'multiple_choice'
    SLIDER = 'slider'

questions = [
    {
        'id': 1,
        'type': QuestionType.SLIDER,
        'text': "Aký je váš rozpočet na darček?",
        'category': "price",
        'options': {
            'min': 0,
            'max': 1000,
            'step': 10
        }
    },
    {
        'id': 2,
        'type': QuestionType.MULTIPLE_CHOICE,
        'text': "Pre koho je darček určený?",
        'category': "recipient",
        'options': ["priateľ/ka", "rodič", "súrodenec", "kolega", "iný"]
    },
    # Tu budú ďalšie otázky
] 