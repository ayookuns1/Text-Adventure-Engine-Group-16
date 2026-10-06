# gui.py - the Tkinter front end for the escape room game
#
# This file is only in charge of DISPLAYING things and reacting to button
# clicks. All the actual game rules live in game.py / puzzles.py / room.py
# etc. Whenever something goes wrong (wrong answer, locked door, missing
# item...) the Game object raises one of our custom exceptions, and we just
# catch it here and show a message - the game doesn't crash.

import tkinter as tk
import threading
from tkinter import messagebox, simpledialog

from game.game import Game
from game.puzzles import ItemPuzzle
from game.exceptions import GameError, HintServiceError, NoHintsLeftError

# ---- basic colour / font setup, kept in one place so it's easy to tweak ----
BG_COLOR = "#1e2128"
PANEL_COLOR = "#262a33"
TEXT_COLOR = "#e8e6e1"
ACCENT_COLOR = "#c98a4b"     # warm amber, used for puzzle text / highlights
GOOD_COLOR = "#7fb069"       # green, used for success messages / "connected"
BAD_COLOR = "#d9695f"        # red, used for error messages / "not connected"
NEUTRAL_COLOR = "#888888"    # grey, used while still checking

FONT_NORMAL = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 12, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")


class EscapeRoomGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Escape Room - Group 16")
        self.root.geometry("1050x680")
        self.root.configure(bg=BG_COLOR)

        self.game = None  # created once a difficulty is picked

        self._build_difficulty_screen()

    # ------------------------------------------------------------------
    # difficulty picker - shown first, replaced by the game layout once
    # the player picks a level
    # ------------------------------------------------------------------
    def _build_difficulty_screen(self):
        self.difficulty_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.difficulty_frame.pack(fill="both", expand=True)

        tk.Label(
            self.difficulty_frame, text="TEXT ADVENTURE PUZZLE ENGINE",
            font=FONT_TITLE, bg=BG_COLOR, fg=ACCENT_COLOR
        ).pack(pady=(80, 10))

        tk.Label(
            self.difficulty_frame, text="Choose a difficulty",
            font=FONT_BOLD, bg=BG_COLOR, fg=TEXT_COLOR
        ).pack(pady=(0, 30))

        btn_frame = tk.Frame(self.difficulty_frame, bg=BG_COLOR)
        btn_frame.pack()

        levels = [
            ("Easy", "easy", "5 attempts per puzzle, unlimited hints"),
            ("Medium", "medium", "3 attempts per puzzle, 3 hints total"),
            ("Hard", "hard", "2 attempts per puzzle, 1 hint total"),
        ]

        for label, key, subtitle in levels:
            card = tk.Frame(btn_frame, bg=PANEL_COLOR, padx=20, pady=15)
            card.pack(side="left", padx=15)

            tk.Button(
                card, text=label, width=14, font=FONT_BOLD,
                command=lambda k=key: self._start_game(k)
            ).pack()
            tk.Label(
                card, text=subtitle, font=("Segoe UI", 9),
                bg=PANEL_COLOR, fg=TEXT_COLOR, wraplength=140
            ).pack(pady=(8, 0))

    def _start_game(self, difficulty):
        self.difficulty_frame.destroy()

        self.game = Game(difficulty=difficulty)

        self._build_layout()
        self._refresh_room()

    def _check_ai_connection(self):
        # runs the real Gemini test call on a background thread so the
        # window doesn't freeze while it waits on the network, then safely
        # hands the result back to the main thread with root.after
        def worker():
            connected, reason = self.game.hint_provider.check_connection()
            self.root.after(0, lambda: self._update_ai_status(connected, reason))

        threading.Thread(target=worker, daemon=True).start()

    def _update_ai_status(self, connected, reason):
        # the window (or this game screen) may have been closed/replaced
        # while the background check was still running - guard against
        # touching widgets that no longer exist
        if not self.ai_status_dot.winfo_exists():
            return

        if connected:
            self.ai_status_dot.config(fg=GOOD_COLOR)
            self.ai_status_label.config(text="AI Hints: connected (Gemini)")
        else:
            self.ai_status_dot.config(fg=BAD_COLOR)
            self.ai_status_label.config(text=f"AI Hints: not connected ({reason})")

    def _new_game(self):
        # confirm first - don't throw away progress by accident
        if not messagebox.askyesno("New Game", "Quit this game and pick a new difficulty?"):
            return
        self.game_frame.destroy()
        self.game = None
        self._build_difficulty_screen()

    def _quit_game(self):
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.root.destroy()
