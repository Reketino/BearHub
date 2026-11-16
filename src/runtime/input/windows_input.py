
import keyboard


class WindowsInputBackend:
    """Handles keyboard input on Windows."""

    def write(self, text: str) -> None:
        keyboard.write(text)
