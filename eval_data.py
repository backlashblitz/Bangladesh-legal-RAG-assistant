"""
Expanded test set: 15 questions across all 5 legal domains.
"""

test_cases = [
    # RTI Act
    {
        "question": "What is the maximum time limit to respond to an information request?",
        "ground_truth": "The authority must provide the information within 20 working days, or 30 days if it concerns life and liberty of a person, within 24 hours."
    },
    {
        "question": "How can a person file a complaint under the RTI Act?",
        "ground_truth": "A person can lodge a complaint to the Information Commission if they receive no information, are aggrieved by an appeal decision, or get no decision within the time limit."
    },
    {
        "question": "Who is responsible for providing information under this Act?",
        "ground_truth": "The designated officer-in-charge of the relevant authority is responsible for providing information to the public."
    },

    # Labour Act
    {
        "question": "What is the maternity benefit period for women workers?",
        "ground_truth": "8 weeks before delivery and 8 weeks after delivery, totaling 16 weeks."
    },
    {
        "question": "Can an employer terminate a pregnant worker?",
        "ground_truth": "An employer cannot terminate a woman worker during her maternity leave period without sufficient cause, and doing so does not deprive her of maternity benefits."
    },
    {
        "question": "What are the working hour limits for adult workers?",
        "ground_truth": "Adult workers should not work more than 8 hours a day or 48 hours a week under normal circumstances, per the Labour Act."
    },

    # Consumer Rights Act
    {
        "question": "What is anti-consumer right practice according to the law?",
        "ground_truth": "Selling at higher than fixed price, selling adulterated goods, selling harmful ingredients, false advertising, not delivering as promised, or delivering less quantity than promised."
    },
    {
        "question": "What can a consumer do if they receive defective goods?",
        "ground_truth": "A consumer can file a complaint with the Directorate of National Consumer Rights Protection regarding defective or adulterated goods."
    },
    {
        "question": "Who enforces consumer rights protection in Bangladesh?",
        "ground_truth": "The Directorate of National Consumer Rights Protection enforces this Act."
    },

    # Anti-Corruption Act
    {
        "question": "How does the Anti-Corruption Commission investigate corruption?",
        "ground_truth": "The Commission has sole power to investigate corruption, can empower officers via gazette notification, and those officers get powers equivalent to an officer-in-charge of a police station."
    },
    {
        "question": "Can a private citizen file a corruption complaint?",
        "ground_truth": "Yes, an aggrieved person or someone on their behalf can file a complaint/application with the Commission."
    },
    {
        "question": "What government bodies must cooperate with the Anti-Corruption Commission?",
        "ground_truth": "Any government authority or organisation under the government must cooperate with the Commission as directed."
    },

    # Income Tax Act
    {
        "question": "What is the tax day deadline for a company?",
        "ground_truth": "The 15th day of the seventh month following the end of the income year, or the 15th of September if that date falls earlier."
    },
    {
        "question": "Who is considered a resident for income tax purposes?",
        "ground_truth": "Generally, an individual who stays in Bangladesh for 182 days or more in an income year (or 90 days plus 365 days over the preceding 4 years) is considered a resident."
    },
    {
        "question": "What happens if a company fails to file tax returns on time?",
        "ground_truth": "Late filing typically results in penalties/fines as specified under the Income Tax Act provisions for non-compliance."
    },

    # Out-of-domain guardrail test
    {
        "question": "What is the capital of France?",
        "ground_truth": "This information is not available in the provided legal documents."
    },
]