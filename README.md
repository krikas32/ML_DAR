# Gift Question AI Model

Tento projekt obsahuje ML model pre výber otázok pre darčekový poradca. Model sa učí s pomocou OpenAI API a je schopný vyberať relevantné otázky na základe predchádzajúcich odpovedí.

## Inštalácia

1. Nainštalujte Node.js (verzia 14 alebo vyššia)
2. Klonujte tento repozitár
3. Nainštalujte závislosti:
```bash
npm install
```
4. Vytvorte súbor `.env` a pridajte do neho váš OpenAI API kľúč:
```
OPENAI_API_KEY=your_api_key_here
MODEL_SAVE_PATH=./models
API_ENDPOINT=http://localhost:3000/api/questions
```

## Použitie

### Trénovanie modelu

Pre spustenie trénovania modelu:
```bash
npm run train
```

Model sa bude trénovať, kým nezíska 3 po sebe idúce úspešné relácie. Každá relácia obsahuje 20 otázok, ktoré sú validované pomocou OpenAI API.

### Použitie natrenovaného modelu

Po dokončení trénovania sa model uloží do priečinka `models`. Tento model môže byť použitý v produkčnom prostredí pre výber otázok.

## Štruktúra projektu

- `src/models/QuestionModel.js` - Implementácia ML modelu
- `src/services/openaiService.js` - Služba pre komunikáciu s OpenAI API
- `src/data/questions.js` - Definícia otázok a ich typov
- `src/train.js` - Skript pre trénovanie modelu

## Typy otázok

Model podporuje tri typy otázok:
- Yes/No (áno/nie)
- Multiple Choice (výber z možností)
- Slider (posuvník s hodnotami)

## API

Po dokončení trénovania model posiela odpovede cez API endpoint definovaný v `.env` súbore. 