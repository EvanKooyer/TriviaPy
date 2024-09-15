from textual import on
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button, Static, Footer, Header
from textual_countdown import Countdown
from textual.message import Message
import time
import requests
import json
import random


# Generator function to pull and parse trivia questions for program use
def get_trivia_questions(num_qs=10, category=None, session_id=None):
    api_response = requests.get(
        'https://opentdb.com/api.php?amount={q}&token={token}'.format(
            q=num_qs, token=session_id)
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


def get_trivia_categories():
    api_response = requests.get('https://opentdb.com/api_category.php')

    api_data = json.loads(api_response.text)['trivia_categories']
    categories = {}

    for category in api_data:
        categories[category['name']] = category['id']

    return categories


def get_api_key():
    api_response = requests.get(
        'https://opentdb.com/api_token.php?command=request')
    key = json.loads(api_response.text)['token']
    return key


class GameFinish(Screen):

    def __init__(self, score, correct, incorrect, id='finish'):
        self.final_score = score
        self.correct_answers = correct
        self.incorrect_answers = incorrect
        super().__init__(id=id)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Label('RESULTS', id='results')
        yield Label('Correct Answers: {correct}'.format(correct=self.correct_answers), id='correct')
        yield Label('Incorrect Answers: {incorrect}'.format(incorrect=self.incorrect_answers), id='incorrect')
        yield Label('Final Score: {score}'.format(score=self.final_score), id='finalscore')
        yield Button('Return to Main Menu', id='return')


class Question(Static):
    # Question class takes in a question and the current score and shows it on screen

    answered = False
    correct = False

    def __init__(self, question, id: str, current_score=0):
        self.question = question
        self.score = current_score
        self.started = time.time()
        super().__init__()

    class Answered(Message):

        def __init__(self, correct: bool, points: int, question) -> None:
            self.correct = correct
            self.points = points
            self.question = question
            super().__init__()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.option_dict[event.button.id] == self.question['correct_answer']:
            self.correct = True
            self.stopped = time.time()
            modifier = round(((30-(self.stopped-self.started))/30), ndigits=4)
            score = int(1000*modifier)
            self.post_message(self.Answered(
                self.correct, score, self.question))
        else:
            self.correct = False
            self.post_message(self.Answered(self.correct, 0, self.question))

    # Don't understand why this decorator works but its the only way my program
    # recognized this event...
    @on(Countdown.Finished)
    def on_countdown_finish(self, event: Countdown.Finished) -> None:
        self.correct = False
        self.post_message(self.Answered(self.correct, 0, self.question))

    def compose(self) -> ComposeResult:
        yield Label(self.question['question'], id='question')

        button_num = 1
        self.option_dict = {}

        for option in self.question['options']:
            self.option_dict['a_' + str(button_num)] = option
            yield Button(option, id=('a_' + str(button_num)))
            button_num += 1
        yield Label('Current Score: {score}'.format(score=self.score))
        # this countdown timer is not quite working well for me, this
        # is the only way i have gotten it to work so far.
        self.cd = Countdown(id='countdown')
        yield self.cd
        self.cd.start(30)


class Game(Screen):

    def __init__(self, gtqs, num_qs, id: str):
        self.gtqs = gtqs
        self.question_ans = 0
        self.score = 0
        self.correct = 0
        self.incorrect = 0
        self.num_qs = num_qs
        super().__init__(id=id)

    class Finished(Message):

        def __init__(self, score, correct, incorrect):
            self.final_score = score
            self.num_correct = correct
            self.num_incorrect = incorrect
            super().__init__()

    def on_question_answered(self, message: Question.Answered) -> None:
        if message.correct is True:
            self.question_ans += 1
            self.correct += 1
            self.score += message.points
        else:
            self.incorrect += 1
            self.question_ans += 1

        if self.question_ans < self.num_qs:
            self.remove_children()
            self.mount(Question(next(self.gtqs),
                       id='q_{num}'.format(num=self.question_ans), current_score=self.score))
        else:
            self.remove_children()
            self.post_message(self.Finished(
                self.score, self.correct, self.incorrect))

    def compose(self) -> ComposeResult:

        yield Header()
        yield Footer()
        yield Question(next(self.gtqs), id='q_{num}'.format(num=self.question_ans))


class OptionScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Label("Enter the number of settings or choose your desired category", id='title')
        yield Input('Desired number of Questions: ', id='numqs', type='integer')


class MainMenu(App):

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'start':
            starttime = str(int(time.time()))
            trivia_qs = get_trivia_questions(
                self.num_qs, session_id=self.api_key)
            self.install_screen(Game(trivia_qs, self.num_qs, id='game_{id}'.format(
                id=starttime)), name='gamescreen')
            self.push_screen('gamescreen')
        elif event.button.id == 'options':
            pass
        elif event.button.id == 'quit':
            self.exit()
        elif event.button.id == 'return':
            self.pop_screen()
            self.uninstall_screen('gamescreen')
            self.uninstall_screen('finishscreen')

    def on_game_finished(self, message: Game.Finished) -> None:
        self.install_screen(GameFinish(
            message.final_score,
            message.num_correct,
            message.num_incorrect), name='finishscreen')
        self.switch_screen('finishscreen')

    def compose(self) -> ComposeResult:

        self.num_qs = 10
        self.trivia_answered = 0
        self.categories = get_trivia_categories()
        self.api_key = get_api_key()

        yield Header()
        yield Footer()
        yield Button('Start Game', id='start')
        yield Button('Change Game Settings', id='options')
        yield Button('Quit', id='quit')


if __name__ == "__main__":
    app = MainMenu()
    app.run()
