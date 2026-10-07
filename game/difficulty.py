]633;E;{ printf '%s\\n' "# Difficulty settings." "# Each level has its own puzzles (see map_builder.py), and also changes the" "# number of attempts allowed per puzzle and how many AI hints you get."\x3b tail -n +4 game/difficulty.py\x3b } > game/difficulty.new && mv game/difficulty.new game/difficulty.py;22b95746-0ce1-4afb-90f2-f4c4bdffbffd]633;C# Difficulty settings.
# Each level has its own puzzles (see map_builder.py), and also changes the
# number of attempts allowed per puzzle and how many AI hints you get.

DIFFICULTY_SETTINGS = {
    "easy": {
        "max_attempts": 5,
        "hint_limit": None,   # None means unlimited hints
    },
    "medium": {
        "max_attempts": 3,
        "hint_limit": 3,
    },
    "hard": {
        "max_attempts": 2,
        "hint_limit": 1,   # only ONE hint for the whole map
    },
}


def get_settings(difficulty):
    difficulty = difficulty.lower().strip()
    if difficulty not in DIFFICULTY_SETTINGS:
        difficulty = "medium"
    return DIFFICULTY_SETTINGS[difficulty]
