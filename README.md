# Escape Room - Group 16

A Tkinter-based escape room game. Pick a difficulty, move through rooms,
solve puzzles, click to pick up items, and get AI hints from the Gemini
API when you're stuck.

## Setup

```bash
pip install -r requirements.txt
```

To enable AI hints, set the `GEMINI_API_KEY` environment variable to your
Gemini API key before running the game (get a free key at
https://aistudio.google.com/app/apikey). Without a key, the Hint button
still works - it just shows the built-in hint instead of an AI-generated one.

A small status indicator at the top of the game screen shows whether the
Gemini connection is actually working - a grey dot while it checks (it
does a real test call in the background on startup), then green ("AI
Hints: connected") if the key works, or red with the reason if it
doesn't (no key set, SDK not installed, bad key, no internet, etc).

## Run

```bash
python gui.py
```

You'll see a difficulty screen first (Easy / Medium / Hard), then the game.

## Difficulty levels

Each difficulty has its OWN puzzles (different riddles/codes) as well as
different attempts and hint limits, so the three levels genuinely feel
different, not just "same riddle, fewer guesses":

| Level  | Attempts per puzzle | AI hints total |
|--------|---------------------|-----------------|
| Easy   | 5                   | Unlimited       |
| Medium | 3                   | 3               |
| Hard   | 2                   | 1               |

Note: a hint (AI-generated OR the static fallback shown when the AI call
fails) always costs one use. On Hard, that means you only get to use the
Hint button once for the entire map, so use it wisely.

### Answer key (for testing / in case you get stuck prepping the demo)

**Easy**
- Entrance: `keyboard`
- Hallway: `footsteps`
- Library code: `1234`
- Workshop: `clock`

**Medium**
- Entrance: `darkness`
- Hallway: `map`
- Library code: `4747` (year of the first recorded computer bug, 1947, last two digits doubled)
- Workshop: `egg`

**Hard**
- Entrance: `machine` (Caesar cipher, shift 3: PDFKLQH -> MACHINE)
- Hallway: `white` (classic "four walls facing south" riddle - only possible at the North Pole, so it's a polar bear)
- Library code: `6590` (ASCII value of 'A' is 65, ASCII value of 'Z' is 90)
- Workshop: `coffin`

**Vault (all levels)**: not a riddle - just needs the Brass Key from the Workshop.

## Files

```
gui.py                  the Tkinter window, all screens and buttons
game/
    exceptions.py        custom exceptions (GameError and subclasses)
    items.py              Item, Inventory
    puzzles.py             Puzzle (base) + RiddlePuzzle, CodePuzzle, ItemPuzzle
    room.py               Room
    player.py              Player
    ai_hint.py             AIHintProvider (Gemini API)
    difficulty.py           attempts/hint settings per difficulty level
    map_builder.py          builds all 6 rooms + puzzles + items
    game.py               Game class, ties everything together
```

## How the rooms connect

Entrance Hall -> Hallway -> Library -> Workshop (side room, has the key)
                                    -> Vault Room -> Exit

Each room has its own puzzle blocking progress. The Workshop's riddle
locks the Brass Key itself (not an exit) - you can always walk back out
of the Workshop, but you can't pick up the key until you solve the riddle.
The Vault needs the key from the Workshop to open.

Map note: the map panel is drawn so "north" visually goes up and "south"
goes down, matching the direction buttons.
