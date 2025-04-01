const questionTypes = {
    YES_NO: 'yes_no',
    MULTIPLE_CHOICE: 'multiple_choice',
    SLIDER: 'slider'
};

const questions = [
    {
        id: 1,
        type: questionTypes.SLIDER,
        text: "Aký je váš rozpočet na darček?",
        category: "price",
        options: {
            min: 0,
            max: 1000,
            step: 10
        }
    },
    {
        id: 2,
        type: questionTypes.MULTIPLE_CHOICE,
        text: "Pre koho je darček určený?",
        category: "recipient",
        options: ["priateľ/ka", "rodič", "súrodenec", "kolega", "iný"]
    },
    // Tu budú ďalšie otázky
];

module.exports = {
    questionTypes,
    questions
}; 