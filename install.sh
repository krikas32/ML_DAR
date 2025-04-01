#!/bin/bash

echo "Inštalácia systému odporúčania darčekov..."

# Kontrola Python verzie
if ! command -v python3 &> /dev/null; then
    echo "Python3 nie je nainštalovaný. Inštalujem Python3..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install python3
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    else
        echo "Nepodporovaný operačný systém"
        exit 1
    fi
fi

# Kontrola CUDA pre GPU
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Kontrolujem CUDA..."
    if ! command -v nvcc &> /dev/null; then
        echo "CUDA nie je nainštalovaná. Inštalujem CUDA..."
        wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
        sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
        wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda-repo-ubuntu2204-12-1-local_12.1.0-530.30.02-1_amd64.deb
        sudo dpkg -i cuda-repo-ubuntu2204-12-1-local_12.1.0-530.30.02-1_amd64.deb
        sudo cp /var/cuda-repo-ubuntu2204-12-1-local/7fa2af80.pub /etc/apt/trusted.gpg.d/
        sudo apt-get update
        sudo apt-get -y install cuda
    fi
fi

# Vytvorenie virtuálneho prostredia
echo "Vytváram virtuálne prostredie..."
python3 -m venv venv
source venv/bin/activate

# Inštalácia pip a upgrade
echo "Inštalujem a aktualizujem pip..."
python3 -m pip install --upgrade pip

# Inštalácia závislostí
echo "Inštalujem závislosti..."
pip install -r requirements.txt

# Vytvorenie .env súboru ak neexistuje
if [ ! -f .env ]; then
    echo "Vytváram .env súbor..."
    cat > .env << EOL
OPENAI_API_KEY=your_openai_api_key_here
DROPBOX_ACCESS_TOKEN=your_dropbox_access_token_here
MODEL_SAVE_PATH=./models
EOL
    echo "Prosím upravte .env súbor a pridajte svoje API kľúče"
fi

# Vytvorenie priečinka pre modely
mkdir -p models

echo "Inštalácia dokončená!"
echo "Pre spustenie aplikácie:"
echo "1. Upravte .env súbor a pridajte svoje API kľúče"
echo "2. Aktivujte virtuálne prostredie: source venv/bin/activate"
echo "3. Spustite trénovanie: python src/train.py"
echo "4. Spustite aplikáciu: python src/app.py" 