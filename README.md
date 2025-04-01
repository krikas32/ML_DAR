# Systém odporúčania darčekov

Tento projekt implementuje systém odporúčania darčekov pomocou strojového učenia. Systém používa neurónovú sieť na výber najvhodnejších otázok pre používateľa a OpenAI API na validáciu výberu otázok.

## Požiadavky

- Python 3.8 alebo novší
- CUDA Toolkit (pre GPU akceleráciu)
- cuDNN (pre GPU akceleráciu)

## Inštalácia

1. Nainštalujte potrebné balíčky:
```bash
pip install -r requirements.txt
```

2. Vytvorte súbor `.env` v koreňovom adresári projektu s nasledujúcimi premennými:
```
OPENAI_API_KEY=your_openai_api_key_here
DROPBOX_ACCESS_TOKEN=your_dropbox_access_token_here
MODEL_SAVE_PATH=./models
```

## Použitie

### Trénovanie modelu
```bash
python src/train.py
```

### Spustenie aplikácie
```bash
python src/app.py
```

## Štruktúra projektu

```
src/
├── data/
│   └── questions.py
├── models/
│   └── question_model.py
├── services/
│   ├── dropbox_service.py
│   └── openai_service.py
├── app.py
└── train.py
```

## GPU podpora

Pre využitie GPU akcelerácie je potrebné:

1. Nainštalovať CUDA Toolkit z [NVIDIA stránky](https://developer.nvidia.com/cuda-downloads)
2. Nainštalovať cuDNN z [NVIDIA stránky](https://developer.nvidia.com/cudnn)
3. Nastaviť premenné prostredia:
```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64
```

## Licencia

MIT 