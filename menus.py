from textual import on
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button, Static, Footer, Header
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual_countdown import Countdown
from textual.message import Message
import main
import time


class GameFinish(Screen):

    def __init__(self, score, correct, incorrect, id):
        self.final_score = score
        self.correct_answers = correct
        self.incorrect_answers = incorrect
        super.__init__(id=id)

    def __compose__(self) -> ComposeResult:
        yield Label('RESULTS', id='results')
        yield Label('Correct Answers: {correct}'.format(correct=self.correct_answers), id='correct')
        yield Label('Incorrect Answers: {incorrect}'.format(incorrect=self.incorrect_answers), id='incorrect')
        yield Label('Final Score: {score}'.format(score=self.final_score))
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
            super.__init__()

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
            self.install_screen(GameFinish(
                self.score, self.correct, self.incorrect, id='finished'))
            self.push_screen('finished')

    def compose(self) -> ComposeResult:

        yield Header()
        yield Footer()
        yield Question(next(self.gtqs), id='q_{num}'.format(num=self.question_ans))


class MainMenu(App):

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'start':
            self.install_screen(
                Game(self.trivia_qs, self.num_qs, id='game'), name='gamescreen')
            self.push_screen('gamescreen')

    def compose(self) -> ComposeResult:

        self.num_qs = 10
        self.trivia_answered = 0

        self.trivia_qs = main.get_trivia_questions(self.num_qs)

        yield Header()
        yield Footer()
        yield Button('Start Game', id='start')


if __name__ == "__main__":
    app = MainMenu()
    app.run()
