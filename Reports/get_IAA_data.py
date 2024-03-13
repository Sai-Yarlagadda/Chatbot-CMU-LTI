import random

with open('questions.txt', 'r') as file:
    questions = file.readlines()

random.shuffle(questions)
sample_questions = questions[:40]

with open('questions_for_IAA.txt', 'w') as output_file:
    for question in sample_questions:
        output_file.write(question)