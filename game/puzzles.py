# Puzzle classes
# Puzzle is the parent/base class. Each type of puzzle below inherits from it
# but checks the answer in a different way - this is our polymorphism example,
# the game just calls puzzle.solve(answer) and doesn't care which type it is.

from game.exceptions import WrongAnswerError, ItemNotFoundError


class Puzzle:
    def __init__(self, prompt, hint, max_attempts=3):
        self.prompt = prompt
        self.hint = hint
        self.max_attempts = max_attempts
        self.attempts_used = 0
        self.solved = False

    def check_answer(self, answer):
        # base version, subclasses should override this
        return False

    def solve(self, answer):
        if self.solved:
            return True

        correct = self.check_answer(answer)
        if correct:
            self.solved = True
            return True
        else:
            self.attempts_used += 1
            attempts_left = self.max_attempts - self.attempts_used
            raise WrongAnswerError(attempts_left)

    def get_hint(self):
        return self.hint


class RiddlePuzzle(Puzzle):
    # solved by typing a word or phrase
    def __init__(self, prompt, answer, hint, max_attempts=3):
        super().__init__(prompt, hint, max_attempts)
        self.answer = answer.lower().strip()

    def check_answer(self, answer):
        return answer.lower().strip() == self.answer


class CodePuzzle(Puzzle):
    # solved by typing a numeric code, like a lock combo
    def __init__(self, prompt, code, hint, max_attempts=4):
        super().__init__(prompt, hint, max_attempts)
        self.code = code.strip()

    def check_answer(self, answer):
        cleaned = answer.strip().replace(" ", "")
        return cleaned == self.code


class ItemPuzzle(Puzzle):
    # solved by using an item from the inventory instead of typing an answer
    def __init__(self, prompt, required_item, hint):
        super().__init__(prompt, hint, max_attempts=99)
        self.required_item = required_item.lower()

    def check_answer(self, answer):
        return answer.lower().strip() == self.required_item

    def solve_with_item(self, inventory):
        if not inventory.has_item(self.required_item):
            raise ItemNotFoundError(self.required_item)
        self.solved = True
        return True
