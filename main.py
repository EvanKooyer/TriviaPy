import requests
import json


def get_trivia_questions(num_qs=10, category='general'):
    api_response = requests.get(
        'https://opentdb.com/api.php?amount={q}'.format(q=num_qs))
    trivia_data = json.loads(api_response.text)

    return trivia_data['results']


trivia_questions = get_trivia_questions()

for question in trivia_questions:
    print(question['category'])
    print(question['difficulty'])
    print(question['question'])
    print('\n')
