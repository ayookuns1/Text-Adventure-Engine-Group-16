# Custom exceptions for the escape room game
# Basic idea: instead of letting Python crash with a generic error, we raise
# our own exceptions so we can catch them and show a nice message in the GUI.

class GameError(Exception):
    # base class, every other exception below inherits from this
    pass


class InvalidDirectionError(GameError):
    def __init__(self, direction):
        self.direction = direction
        super().__init__(f"You can't go {direction} from here.")


class LockedRoomError(GameError):
    def __init__(self, room_name):
        super().__init__(f"You need to solve the puzzle in {room_name} first.")


class ItemNotFoundError(GameError):
    def __init__(self, item_name):
        super().__init__(f"There's no '{item_name}' here.")


class WrongAnswerError(GameError):
    def __init__(self, attempts_left):
        self.attempts_left = attempts_left
        super().__init__(f"Wrong answer. Attempts left: {attempts_left}")


class InventoryFullError(GameError):
    def __init__(self, capacity):
        super().__init__(f"Inventory is full. Max {capacity} items.")


class HintServiceError(GameError):
    # raised when the Gemini API call fails for any reason
    # (no internet, bad key, timeout etc). We always catch this
    # and show a normal hint instead so the game doesn't break.
    pass


class NoHintsLeftError(GameError):
    # raised when the player has used up all their hints for the
    # difficulty level they picked (mainly relevant on Hard, which only
    # allows 1 hint for the whole map)
    def __init__(self):
        super().__init__("You're out of hints for this difficulty level.")
