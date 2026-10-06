# This file builds the whole game map - all the rooms, puzzles and items.
# Keeping this separate from game.py means we can add/change rooms here
# without touching the actual game logic.
#
# Each difficulty level has its OWN set of puzzle content (different
# riddles/codes, not just different attempt counts) so Easy, Medium and
# Hard actually feel different to play, not just "the same puzzle with
# fewer guesses". The rooms themselves and how they connect stay the same
# across all three levels - only the puzzles inside them change.

from game.room import Room
from game.items import Item
from game.puzzles import RiddlePuzzle, CodePuzzle, ItemPuzzle
from game.difficulty import get_settings


# ---------------- puzzle content per difficulty ----------------
# each entry is (prompt, answer, hint) for the 3 riddle/code puzzles.
# the vault's item puzzle doesn't change - it's not a riddle.

PUZZLE_SETS = {
    "easy": {
        "entrance": (
            "A plaque says: 'I have keys but no locks, space but no room. What am I?'",
            "keyboard",
            "You're probably using one right now to type.",
        ),
        "hallway": (
            "Written on the wall: 'The more you take, the more you leave behind. What am I?'",
            "footsteps",
            "Think about walking.",
        ),
        "library": (
            "A lockbox needs a 4 digit code. A sticky note on the front just says: '1-2-3-4'.",
            "1234",
            "It's written right there on the note.",
        ),
        "workshop": (
            "A sign reads: 'I have a face and two hands but no arms or legs. What am I?'",
            "clock",
            "It's something you check to know the time.",
        ),
    },
    "medium": {
        "entrance": (
            "A plaque says: 'The more of me there is, the less you see. What am I?'",
            "darkness",
            "Think about what happens when you turn off the lights.",
        ),
        "hallway": (
            "Written on the wall: 'I have cities but no houses, forests but no trees, "
            "water but no fish. What am I?'",
            "map",
            "You'd use it to find your way somewhere.",
        ),
        "library": (
            "A lockbox needs a 4 digit code. Note: 'Year of the first recorded computer "
            "bug, last 2 digits doubled.'",
            "4747",
            "Look up when the first computer bug was recorded (it's a famous story "
            "involving an actual moth), then double the last two digits of that year.",
        ),
        "workshop": (
            "A sign reads: 'What has to be broken before you can use it?'",
            "egg",
            "Think about breakfast.",
        ),
    },
    "hard": {
        "entrance": (
            "A message is carved into the wall, shifted by 3 letters (Caesar cipher): "
            "'PDFKLQH'",
            "machine",
            "Shift each letter back by 3 in the alphabet (P->M, D->A, and so on).",
        ),
        "hallway": (
            "A riddle is etched into the floor: 'A man built a house with four walls, "
            "each one facing south. A bear walks past. What color is the bear?'",
            "white",
            "Think about WHERE on Earth every wall could possibly face south at once.",
        ),
        "library": (
            "A lockbox needs a 4 digit code. Note: 'The ASCII code for the first letter "
            "of the alphabet, followed by the ASCII code for the last.'",
            "6590",
            "Look up the ASCII value of the letter A, then the ASCII value of the "
            "letter Z, and put them next to each other.",
        ),
        "workshop": (
            "A sign reads: 'The person who makes it, sells it. The person who buys it, "
            "never uses it. The person who uses it, never knows it. What is it?'",
            "coffin",
            "Think about something made for someone else, after they're gone.",
        ),
    },
}
