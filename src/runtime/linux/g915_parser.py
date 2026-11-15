
from dataclasses import dataclass


REPORT_ID = 0x01
REPORT_LENGTH = 17


G_KEY_MAPPING = {
    "G1": (14, 0x10),
    "G2": (14, 0x20),
    "G3": (14, 0x40),
    "G4": (14, 0x80),
    "G5": (15, 0x01),
    "G6": (15, 0x02),
    "G7": (15, 0x04),
    "G8": (15, 0x08),
    "G9": (15, 0x10),
}


@dataclass(frozen=True)
class G915XEvent:
    """Represents a G-key press or release event."""

    key: str
    pressed: bool


class G915XParser:
    """Parse G-key events from Logitech G915 X HID reports."""

    def __init__(self):
        self._previous_pressed: set[str] = set()

    def parse_report(self, report: bytes) -> list[G915XEvent]:
        """Parse a HID report and return detected key state changes."""

        if len(report) != REPORT_LENGTH:
            return []

        if report[0] != REPORT_ID:
            return []

        current_pressed = self._get_pressed_keys(report)

        newly_pressed = current_pressed - self._previous_pressed
        newly_released = self._previous_pressed - current_pressed

        events = []

        for key in G_KEY_MAPPING:
            if key in newly_pressed:
                events.append(G915XEvent(key, True))

            if key in newly_released:
                events.append(G915XEvent(key, False))

        self._previous_pressed = current_pressed

        return events

    @staticmethod
    def _get_pressed_keys(report: bytes) -> set[str]:
        """Extract currently pressed G-keys from a HID report."""

        return {
            key
            for key, (byte_index, mask) in G_KEY_MAPPING.items()
            if report[byte_index] & mask
        }

    def release_all(self) -> list[G915XEvent]:
        """Generate release events for every currently held G-key."""

        events = [
            G915XEvent(key, False)
            for key in G_KEY_MAPPING
            if key in self._previous_pressed
        ]

        self._previous_pressed.clear()

        return events

    def reset(self) -> None:
        """Reset the parser without generating release events."""

        self._previous_pressed.clear()
