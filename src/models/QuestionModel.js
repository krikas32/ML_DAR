const tf = require('@tensorflow/tfjs-node');
const fs = require('fs');
const path = require('path');
const { questionTypes } = require('../data/questions');
const DropboxService = require('../services/dropboxService');

class QuestionModel {
    constructor() {
        this.model = null;
        this.consecutiveSuccesses = 0;
        this.requiredSuccesses = 3;
        this.modelPath = path.join(process.env.MODEL_SAVE_PATH, 'question_model');
        this.dropbox = new DropboxService();
    }

    async buildModel() {
        console.log('Vytváram nový model...');
        this.model = tf.sequential({
            layers: [
                tf.layers.dense({ inputShape: [150], units: 64, activation: 'relu' }),
                tf.layers.dropout({ rate: 0.2 }),
                tf.layers.dense({ units: 32, activation: 'relu' }),
                tf.layers.dropout({ rate: 0.2 }),
                tf.layers.dense({ units: 20, activation: 'softmax' })
            ]
        });

        this.model.compile({
            optimizer: tf.train.adam(0.001),
            loss: 'categoricalCrossentropy',
            metrics: ['accuracy']
        });
        console.log('Model bol úspešne vytvorený');
    }

    async selectNextQuestion(previousAnswers, availableQuestions) {
        if (!this.model) {
            await this.buildModel();
        }

        // Konvertujeme predchádzajúce odpovede na tensor
        const inputTensor = this.preprocessAnswers(previousAnswers);
        
        // Predikujeme ďalšiu otázku
        const prediction = await this.model.predict(inputTensor).data();
        
        // Vyberieme otázku s najvyššou pravdepodobnosťou
        const selectedQuestionIndex = this.getHighestProbabilityIndex(prediction);
        return availableQuestions[selectedQuestionIndex];
    }

    preprocessAnswers(answers) {
        // Konvertujeme odpovede na vektor
        const vector = new Array(150).fill(0);
        answers.forEach((answer, index) => {
            vector[index] = this.normalizeAnswer(answer);
        });
        return tf.tensor2d([vector]);
    }

    normalizeAnswer(answer) {
        switch (answer.type) {
            case questionTypes.YES_NO:
                return answer.value ? 1 : 0;
            case questionTypes.SLIDER:
                return answer.value / answer.max;
            case questionTypes.MULTIPLE_CHOICE:
                return answer.selectedIndex / answer.options.length;
            default:
                return 0;
        }
    }

    getHighestProbabilityIndex(prediction) {
        return prediction.indexOf(Math.max(...prediction));
    }

    async saveModel() {
        if (!this.model) {
            throw new Error('Model nie je inicializovaný');
        }

        try {
            // Vytvoríme priečinok ak neexistuje
            if (!fs.existsSync(process.env.MODEL_SAVE_PATH)) {
                fs.mkdirSync(process.env.MODEL_SAVE_PATH, { recursive: true });
            }

            // Uložíme model lokálne
            await this.model.save(`file://${this.modelPath}`);
            
            // Overíme či sa súbory skutočne vytvorili
            const modelFiles = ['model.json', 'weights.bin'];
            const allFilesExist = modelFiles.every(file => 
                fs.existsSync(path.join(this.modelPath, file))
            );

            if (!allFilesExist) {
                throw new Error('Niektoré súbory modelu sa neuložili správne');
            }

            // Nahrajeme model na Dropbox
            await this.dropbox.initialize();
            const uploaded = await this.dropbox.uploadModel(this.modelPath);

            if (!uploaded) {
                throw new Error('Chyba pri nahrávaní modelu na Dropbox');
            }

            console.log('Model bol úspešne uložený lokálne a na Dropbox');
            return true;
        } catch (error) {
            console.error('Chyba pri ukladaní modelu:', error);
            return false;
        }
    }

    async loadModel() {
        try {
            // Skúsime načítať model z Dropboxu
            await this.dropbox.initialize();
            const downloaded = await this.dropbox.downloadModel(this.modelPath);

            if (!downloaded) {
                console.log('Žiadny model nebol nájdený na Dropboxe, vytváram nový...');
                await this.buildModel();
                return false;
            }

            console.log('Načítavam model z Dropboxu...');
            this.model = await tf.loadLayersModel(`file://${this.modelPath}/model.json`);
            console.log('Model bol úspešne načítaný');
            return true;
        } catch (error) {
            console.error('Chyba pri načítaní modelu:', error);
            console.log('Vytváram nový model...');
            await this.buildModel();
            return false;
        }
    }
}

module.exports = QuestionModel; 