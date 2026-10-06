# Player class

from game.items import Inventory


class Player:
    def __init__(self, starting_room):
        self.current_room = starting_room
        self.inventory = Inventory()
        self.moves = 0
        self.score = 0
        self.hints_used = 0
        self.visited_rooms = set()
        self.visited_rooms.add(starting_room.name)

    def move_to(self, room):
        self.current_room = room
        self.moves += 1
        self.visited_rooms.add(room.name)

    def add_score(self, points):
        self.score += points
