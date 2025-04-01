const OpenAI = require('openai');
require('dotenv').config();

class OpenAIService {
    constructor() {
        if (!process.env.OPENAI_API_KEY) {
            throw new Error('OPENAI_API_KEY nie je nastavený v .env súbore');
        }

        this.openai = new OpenAI({
            apiKey: process.env.OPENAI_API_KEY
        });
    }

    async validateQuestionSelection(selectedQuestion, previousAnswers) {
        try {
            // Najprv otestujeme API kľúč
            await this.testAPIKey();
            
            const prompt = this.createValidationPrompt(selectedQuestion, previousAnswers);
            
            const response = await this.openai.chat.completions.create({
                model: "gpt-4",
                messages: [
                    {
                        role: "system",
                        content: "Si expert na výber otázok pre darčekový poradca. Tvoja úloha je validovať, či je vybraná otázka relevantná a užitočná pre získanie informácií o preferenciách pre darček."
                    },
                    {
                        role: "user",
                        content: prompt
                    }
                ],
                temperature: 0.7,
                max_tokens: 150
            });

            const validation = response.choices[0].message.content;
            return this.parseValidationResponse(validation);
        } catch (error) {
            console.error('Chyba pri validácii otázky s OpenAI:', error);
            if (error.response?.status === 401) {
                console.error('Neplatný OpenAI API kľúč. Skontrolujte .env súbor.');
            }
            return false;
        }
    }

    async testAPIKey() {
        try {
            await this.openai.chat.completions.create({
                model: "gpt-4",
                messages: [{ role: "user", content: "Test" }],
                max_tokens: 5
            });
            console.log('OpenAI API kľúč je platný');
            return true;
        } catch (error) {
            if (error.response?.status === 401) {
                throw new Error('Neplatný OpenAI API kľúč');
            }
            throw error;
        }
    }

    createValidationPrompt(selectedQuestion, previousAnswers) {
        return `
        Predchádzajúce odpovede: ${JSON.stringify(previousAnswers)}
        Vybraná otázka: ${JSON.stringify(selectedQuestion)}
        
        Je táto otázka relevantná a užitočná pre získanie informácií o preferenciách pre darček?
        Odpovedz len "ÁNO" alebo "NIE".
        `;
    }

    parseValidationResponse(response) {
        return response.trim().toUpperCase() === 'ÁNO';
    }
}

module.exports = OpenAIService; 