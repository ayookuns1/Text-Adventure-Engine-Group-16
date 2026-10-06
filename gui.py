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

    # ------------------------------------------------------------------
    # building the layout
    # ------------------------------------------------------------------
    def _build_layout(self):
        # everything for the game screen lives inside this one frame, so
        # we can destroy it in one shot when the player starts a new game
        self.game_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.game_frame.pack(fill="both", expand=True)

        # top title bar + menu buttons (New Game / Quit)
        title_frame = tk.Frame(self.game_frame, bg=BG_COLOR)
        title_frame.pack(fill="x", pady=(10, 5))

        tk.Label(
            title_frame, text="TEXT ADVENTURE PUZZLE ENGINE",
            font=FONT_TITLE, bg=BG_COLOR, fg=ACCENT_COLOR
        ).pack(side="left", padx=(20, 0), expand=True)

        menu_frame = tk.Frame(title_frame, bg=BG_COLOR)
        menu_frame.pack(side="right", padx=20)
        tk.Button(menu_frame, text="New Game", width=10, command=self._new_game).pack(side="left", padx=4)
        tk.Button(menu_frame, text="Quit", width=8, command=self._quit_game).pack(side="left", padx=4)

        # ---- Gemini connection indicator ----
        # small coloured dot + label showing whether the AI hint feature is
        # actually working. Starts grey ("checking..."), then the real
        # check runs in a background thread so it doesn't freeze the GUI
        # while it waits on the network, and updates to green/red when done.
        ai_status_frame = tk.Frame(self.game_frame, bg=BG_COLOR)
        ai_status_frame.pack(fill="x", padx=20, pady=(0, 5))

        self.ai_status_dot = tk.Label(
            ai_status_frame, text="\u25cf", font=("Segoe UI", 11),
            bg=BG_COLOR, fg=NEUTRAL_COLOR
        )
        self.ai_status_dot.pack(side="left")

        self.ai_status_label = tk.Label(
            ai_status_frame, text="AI Hints: checking connection...",
            font=("Segoe UI", 9), bg=BG_COLOR, fg=TEXT_COLOR
        )
        self.ai_status_label.pack(side="left", padx=(5, 0))

        self._check_ai_connection()

        # main area split into left (room info) and right (map + inventory)
        main_frame = tk.Frame(self.game_frame, bg=BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        left_frame = tk.Frame(main_frame, bg=BG_COLOR)
        left_frame.pack(side="left", fill="both", expand=True)

        right_frame = tk.Frame(main_frame, bg=BG_COLOR, width=280)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)

        # ---- room description box ----
        self.room_name_label = tk.Label(
            left_frame, text="", font=FONT_BOLD, bg=BG_COLOR, fg=TEXT_COLOR
        )
        self.room_name_label.pack(anchor="w")

        self.room_text = tk.Text(
            left_frame, height=8, wrap="word", bg=PANEL_COLOR, fg=TEXT_COLOR,
            font=FONT_NORMAL, relief="flat", padx=10, pady=10
        )
        self.room_text.pack(fill="both", expand=True, pady=(5, 5))
        self.room_text.config(state="disabled")

        # ---- items in this room - clickable buttons, one per item ----
        # (replaces the old "type the item name" dialog)
        self.items_frame = tk.Frame(left_frame, bg=BG_COLOR)
        self.items_frame.pack(fill="x", pady=(0, 10))

        # ---- direction buttons ----
        move_frame = tk.Frame(left_frame, bg=BG_COLOR)
        move_frame.pack(pady=(0, 10))

        tk.Button(move_frame, text="North", width=10, command=lambda: self._move("north")).grid(row=0, column=1)
        tk.Button(move_frame, text="West", width=10, command=lambda: self._move("west")).grid(row=1, column=0)
        tk.Button(move_frame, text="East", width=10, command=lambda: self._move("east")).grid(row=1, column=2)
        tk.Button(move_frame, text="South", width=10, command=lambda: self._move("south")).grid(row=2, column=1)

        # ---- action buttons ----
        action_frame = tk.Frame(left_frame, bg=BG_COLOR)
        action_frame.pack(pady=(0, 10))

        tk.Button(action_frame, text="Solve Puzzle", width=14, command=self._solve_puzzle).grid(row=0, column=0, padx=4)
        tk.Button(action_frame, text="Use Item", width=14, command=self._use_item).grid(row=0, column=1, padx=4)
        tk.Button(action_frame, text="Hint", width=14, command=self._get_hint, bg=ACCENT_COLOR).grid(row=0, column=2, padx=4)

        # ---- status bar (moves / score) ----
        self.status_label = tk.Label(
            left_frame, text="", font=FONT_NORMAL, bg=BG_COLOR, fg=TEXT_COLOR
        )
        self.status_label.pack(anchor="w")

        # ---- right side: map + inventory ----
        tk.Label(right_frame, text="MAP", font=FONT_BOLD, bg=BG_COLOR, fg=ACCENT_COLOR).pack(anchor="w")
        self.map_canvas = tk.Canvas(right_frame, bg=PANEL_COLOR, height=400, highlightthickness=0)
        self.map_canvas.pack(fill="x", pady=(5, 15))

        tk.Label(right_frame, text="INVENTORY", font=FONT_BOLD, bg=BG_COLOR, fg=ACCENT_COLOR).pack(anchor="w")
        self.inventory_listbox = tk.Listbox(
            right_frame, bg=PANEL_COLOR, fg=TEXT_COLOR, relief="flat",
            font=FONT_NORMAL, height=8
        )
        self.inventory_listbox.pack(fill="x", pady=(5, 15))

        save_frame = tk.Frame(right_frame, bg=BG_COLOR)
        save_frame.pack(fill="x")
        tk.Button(save_frame, text="Save", width=10, command=self._save_game).pack(side="left", padx=(0, 5))
        tk.Button(save_frame, text="Load", width=10, command=self._load_game).pack(side="left")

    # ------------------------------------------------------------------
    # refreshing the screen
    # ------------------------------------------------------------------
    def _refresh_room(self):
        room = self.game.get_current_room()

        self.room_name_label.config(text=room.name)

        self.room_text.config(state="normal")
        self.room_text.delete("1.0", tk.END)
        self.room_text.insert(tk.END, room.describe())
        self.room_text.config(state="disabled")

        self._refresh_items()
        self._refresh_inventory()
        self._refresh_status()
        self._draw_map()

        if self.game.won:
            messagebox.showinfo("You escaped!", f"You made it out!\n\nMoves: {self.game.player.moves}\nScore: {self.game.player.score}")

    def _refresh_items(self):
        # rebuild the row of "take item" buttons for whatever is in the
        # current room - clears out the old buttons first
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        room = self.game.get_current_room()

        # if the room's puzzle guards the items, don't show them until
        # the puzzle is solved (otherwise it spoils the puzzle - you'd
        # see the item sitting there behind a "locked" message)
        if room.guards_items and room.puzzle and not room.puzzle.solved:
            return

        if not room.items:
            return

        tk.Label(
            self.items_frame, text="Take:", font=FONT_NORMAL,
            bg=BG_COLOR, fg=TEXT_COLOR
        ).pack(side="left", padx=(0, 8))

        for item in room.items:
            tk.Button(
                self.items_frame, text=item.name,
                command=lambda name=item.name: self._take_item_by_name(name)
            ).pack(side="left", padx=3)

    def _refresh_inventory(self):
        self.inventory_listbox.delete(0, tk.END)
        for name in self.game.player.inventory.get_names():
            self.inventory_listbox.insert(tk.END, name)

    def _refresh_status(self):
        p = self.game.player
        remaining = self.game.hints_remaining()
        hints_text = "unlimited" if remaining is None else str(remaining)
        self.status_label.config(
            text=f"Difficulty: {self.game.difficulty.title()}   "
                 f"Moves: {p.moves}   Score: {p.score}   Hints left: {hints_text}"
        )
