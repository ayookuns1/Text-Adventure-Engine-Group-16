# AIHintProvider - sends the current puzzle to the Gemini API and gets back a hint.
#
# IMPORTANT: put your Gemini API key below where it says PUT_YOUR_API_KEY_HERE
# You can get a free key from https://aistudio.google.com/app/apikey
#
# If the key is missing or the request fails for any reason (no internet,
# bad key, rate limit, timeout) we raise HintServiceError. The game always
# catches this and just shows the puzzle's normal built-in hint instead,
# so a bad connection never breaks the game.

from game.exceptions import HintServiceError

GEMINI_API_KEY = "PUT_YOUR_API_KEY_HERE"

try:
    import google.generativeai as genai
    SDK_INSTALLED = True
except ImportError:
    SDK_INSTALLED = False


class AIHintProvider:
    def __init__(self):
        self.configured = False

    def _setup(self):
        if self.configured:
            return
        if not SDK_INSTALLED:
            raise HintServiceError("google-generativeai is not installed")
        if GEMINI_API_KEY == "PUT_YOUR_API_KEY_HERE" or not GEMINI_API_KEY:
            raise HintServiceError("No Gemini API key has been set yet")

        try:
            genai.configure(api_key=GEMINI_API_KEY)
        except Exception as e:
            raise HintServiceError(f"Could not set up Gemini: {e}")

        self.configured = True

    def get_ai_hint(self, puzzle_prompt, room_description):
        self._setup()

        prompt = (
            "You are helping a player in a text based escape room game. "
            "Give a short hint (1-2 sentences) for the puzzle below. "
            "Do NOT give away the exact answer, just point them in the right direction.\n\n"
            f"Room: {room_description}\n"
            f"Puzzle: {puzzle_prompt}"
        )

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
        except Exception as e:
            raise HintServiceError(f"Gemini request failed: {e}")

        if not response.text:
            raise HintServiceError("Gemini returned nothing")

        return response.text.strip()

    def check_connection(self):
        """
        Does a real (tiny, cheap) test call to Gemini to confirm the key
        actually works - not just that one is typed in. Used for the
        "AI Hints: connected" indicator in the GUI.

        Returns (True, "") if it works, or (False, reason) if not.
        This never raises - it's meant to be safe to call on startup
        without needing a try/except at the call site.
        """
        try:
            self._setup()
        except HintServiceError as e:
            return False, str(e)

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content("Reply with just the word: OK")
            if response.text and response.text.strip():
                return True, ""
            return False, "Gemini returned an empty response"
        except Exception as e:
            return False, f"Gemini request failed: {e}"
