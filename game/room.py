# Room class

from game.exceptions import InvalidDirectionError, LockedRoomError, ItemNotFoundError


class Room:
    def __init__(self, name, description, puzzle=None, items=None, pos=(0, 0),
                 guarded_exit=None, guards_items=False):
        self.name = name
        self.description = description
        self.puzzle = puzzle
        self.items = items if items else []
        self.exits = {}   # e.g. {"north": <Room object>}
        self.pos = pos     # (x, y) grid position, used for drawing the map

        # guarded_exit is the ONE direction that the puzzle actually blocks.
        # every other exit (like the way you came in) is always free, so
        # you can never get stuck in a room with no way back out.
        self.guarded_exit = guarded_exit

        # guards_items = True means the puzzle blocks picking up items in
        # this room instead of (or as well as) blocking an exit. Used for
        # the Workshop, where the key is locked behind the riddle.
        self.guards_items = guards_items

    def connect(self, direction, room):
        self.exits[direction] = room

    def is_locked(self, direction):
        if self.puzzle is None:
            return False
        if direction != self.guarded_exit:
            return False
        return not self.puzzle.solved

    def get_exit(self, direction):
        if direction not in self.exits:
            raise InvalidDirectionError(direction)
        if self.is_locked(direction):
            raise LockedRoomError(self.name)
        return self.exits[direction]

    def take_item(self, item_name):
        if self.guards_items and self.puzzle and not self.puzzle.solved:
            raise LockedRoomError(self.name)

        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return item
        raise ItemNotFoundError(item_name)

    def describe(self):
        text = self.description
        if self.items and not (self.guards_items and self.puzzle and not self.puzzle.solved):
            names = ", ".join(i.name for i in self.items)
            text += f"\n\nItems here: {names}"
        if self.puzzle and not self.puzzle.solved:
            text += f"\n\nPuzzle: {self.puzzle.prompt}"
        return text
