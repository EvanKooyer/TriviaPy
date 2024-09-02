import requests
import json
import random

session_token = None


# Generator function to pull and parse trivia questions for program use
def get_trivia_questions(num_qs=10, category='general'):
    api_response = requests.get(
        'https://opentdb.com/api.php?amount={q}'.format(q=num_qs)
    )

    trivia_data = json.loads(api_response.text)

    for question in trivia_data['results']:
        options = list(question['incorrect_answers'])
        options.append(question['correct_answer'])
        random.shuffle(options)

        question_dict = {
            'category': question['category'],
            'difficulty': question['difficulty'],
            'question': question['question'],
            'options': options,
            'correct_answer': question['correct_answer']
        }
        yield question_dict


'''
trivia_questions = get_trivia_questions()

num_right = 0
num_wrong = 0

for question in trivia_questions:
    print('Category: ' + question['category'] + '\n')
    print('Difficulty: ' + question['difficulty'] + '\n')
    print(question['question'] + '\n')

    for option in question['options']:
        print('\t' + option)

    response = str(input('\n write your response here: '))

    if response.upper() == question['correct_answer'].upper():
        print('Correct!! \n \n')
        num_right += 1
    else:
        print('WRONG!! \n \n')
        num_wrong += 1

print('You got {correct} questions right, and {incorrect} wrong.'.format(
    correct=num_right, incorrect=num_wrong))

'''
