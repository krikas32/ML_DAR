require('dotenv').config();
const QuestionModel = require('./models/QuestionModel');
const OpenAIService = require('./services/openaiService');
const { questions } = require('./data/questions');
const axios = require('axios');

class ModelTrainer {
    constructor() {
        this.model = new QuestionModel();
        this.openaiService = new OpenAIService();
        this.maxQuestionsPerSession = 20;
    }

    async initialize() {
        console.log('Inicializácia trénovania...');
        
        // Overenie OpenAI API
        try {
            await this.openaiService.testAPIKey();
        } catch (error) {
            console.error('Chyba pri overovaní OpenAI API:', error.message);
            process.exit(1);
        }

        // Overenie modelu
        const modelLoaded = await this.model.loadModel();
        if (!modelLoaded) {
            console.log('Vytváram nový model...');
        }

        // Overenie otázok
        if (questions.length === 0) {
            console.error('Žiadne otázky nie sú definované v questions.js');
            process.exit(1);
        }

        console.log(`Načítaných ${questions.length} otázok`);
    }

    async train() {
        try {
            await this.initialize();
            console.log('Začínam trénovanie modelu...');

            while (this.model.consecutiveSuccesses < this.model.requiredSuccesses) {
                console.log(`\nZačínam novú reláciu (${this.model.consecutiveSuccesses + 1}/${this.model.requiredSuccesses})`);
                
                const sessionSuccess = await this.runTrainingSession();
                
                if (sessionSuccess) {
                    this.model.consecutiveSuccesses++;
                    console.log(`Relácia úspešná! Celkový počet úspešných relácií: ${this.model.consecutiveSuccesses}`);
                    
                    // Uložíme model po každej úspešnej relácii
                    const saved = await this.model.saveModel();
                    if (!saved) {
                        console.error('Chyba pri ukladaní modelu po úspešnej relácii');
                        this.model.consecutiveSuccesses = 0;
                        continue;
                    }
                } else {
                    this.model.consecutiveSuccesses = 0;
                    console.log('Relácia neúspešná, začínam od začiatku.');
                }
            }

            console.log('\nTrénovanie dokončené! Ukladám finálny model...');
            const saved = await this.model.saveModel();
            if (!saved) {
                throw new Error('Chyba pri ukladaní finálneho modelu');
            }
            console.log('Model bol úspešne uložený.');
        } catch (error) {
            console.error('Kritická chyba pri trénovaní:', error);
            process.exit(1);
        }
    }

    async runTrainingSession() {
        const previousAnswers = [];
        let sessionSuccess = true;

        for (let i = 0; i < this.maxQuestionsPerSession; i++) {
            const availableQuestions = this.getAvailableQuestions(previousAnswers);
            if (availableQuestions.length === 0) {
                console.log('Žiadne dostupné otázky pre ďalšiu iteráciu');
                return false;
            }

            const selectedQuestion = await this.model.selectNextQuestion(previousAnswers, availableQuestions);
            
            try {
                const isValid = await this.openaiService.validateQuestionSelection(selectedQuestion, previousAnswers);
                
                if (!isValid) {
                    sessionSuccess = false;
                    break;
                }

                // Simulujeme odpoveď
                const answer = this.generateSimulatedAnswer(selectedQuestion);
                previousAnswers.push(answer);
            } catch (error) {
                console.error('Chyba pri validácii otázky:', error);
                sessionSuccess = false;
                break;
            }
        }

        return sessionSuccess;
    }

    getAvailableQuestions(previousAnswers) {
        const answeredIds = previousAnswers.map(a => a.questionId);
        return questions.filter(q => !answeredIds.includes(q.id));
    }

    generateSimulatedAnswer(question) {
        let value;
        switch (question.type) {
            case 'yes_no':
                value = Math.random() > 0.5;
                break;
            case 'slider':
                value = Math.floor(Math.random() * (question.options.max - question.options.min + 1)) + question.options.min;
                break;
            case 'multiple_choice':
                value = Math.floor(Math.random() * question.options.length);
                break;
        }

        return {
            questionId: question.id,
            type: question.type,
            value: value
        };
    }
}

// Spustenie trénovania
const trainer = new ModelTrainer();
trainer.train().catch(error => {
    console.error('Kritická chyba:', error);
    process.exit(1);
}); 