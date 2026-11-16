
from typing import Protocol


class InputBackend(Protocol):
    """Contract for platform-specific keyboard input backends."""

    def write(self, text: str) -> None:
        """Write text to the currently focused application."""
        ...
