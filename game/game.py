# Game class
# This holds the actual game logic (moving, taking items, solving puzzles).
# It doesn't know anything about Tkinter - the GUI file calls these methods
# and displays whatever they return. Keeping it separate like this means
# the same game logic could work with a text interface OR a GUI.

import json

from game.map_builder import build_map
from game.player import Player
from game.puzzles import ItemPuzzle
from game.ai_hint import AIHintProvider
from game.difficulty import get_settings
from game.exceptions import GameError, ItemNotFoundError, NoHintsLeftError

SAVE_FILE = "savegame.json"


class Game:
    def __init__(self, difficulty="medium"):
        self.difficulty = difficulty
        self.settings = get_settings(difficulty)

        self.start_room = build_map(difficulty)
        self.player = Player(self.start_room)
        self.hint_provider = AIHintProvider()
        self.won = False

    def get_current_room(self):
        return self.player.current_room

    def move(self, direction):
        next_room = self.player.current_room.get_exit(direction)  # can raise
        self.player.move_to(next_room)
        if next_room.name == "Exit":
            self.won = True
        return next_room

    def take_item(self, item_name):
        room = self.player.current_room
        item = room.take_item(item_name)          # can raise ItemNotFoundError
        self.player.inventory.add_item(item)       # can raise InventoryFullError
        return item

    def solve_puzzle(self, answer):
        room = self.player.current_room
        if room.puzzle is None:
            raise GameError("There is nothing to solve in this room.")
        if room.puzzle.solved:
            raise GameError("This puzzle is already solved.")
        if isinstance(room.puzzle, ItemPuzzle):
            raise GameError("This puzzle needs an item, not an answer. Try using an item instead.")

        room.puzzle.solve(answer)   # can raise WrongAnswerError
        self.player.add_score(10)
        return True

    def use_item(self, item_name):
        room = self.player.current_room
        if not isinstance(room.puzzle, ItemPuzzle):
            raise GameError("There's nothing to use an item on here.")
        if not self.player.inventory.has_item(item_name):
            raise ItemNotFoundError(item_name)

        room.puzzle.solve_with_item(self.player.inventory)
        self.player.add_score(15)
        return True
