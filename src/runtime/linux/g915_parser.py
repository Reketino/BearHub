
from dataclasses import dataclass


REPORT_ID = 0x11
REPORT_LENGTH = 20
G_KEY_BYTE_INDEX = 4


G_KEY_MAPPING = {
    0x09: "G1",
    0x06: "G2",
    0x03: "G3",
    0x02: "G4",
    0x07: "G5",
    0x04: "G6",
    0x08: "G7",
    0x05: "G8",
    0x0A: "G9",
}


@dataclass(frozen=True)
class G915XEvent:
    """Represents a G-key press or release event."""

    key: str
    pressed: bool


class G915XParser:
    """Parse G-key events from Logitech G915 X HID reports."""

    def __init__(self):
        self._previous_pressed: str | None = None

    def parse_report(self, report: bytes) -> list[G915XEvent]:
        """Parse a HID report and return detected key state changes."""

        if len(report) != REPORT_LENGTH:
            return []

        if report[0] != REPORT_ID:
            return []

        key_code = report[G_KEY_BYTE_INDEX]

        current_pressed = G_KEY_MAPPING.get(key_code)

        if current_pressed == self._previous_pressed:
            return []

        events = []

        if self._previous_pressed is not None:
            events.append(
                G915XEvent(
                    key=self._previous_pressed,
                    pressed=False,
                )
            )

        if current_pressed is not None:
            events.append(
                G915XEvent(
                    key=current_pressed,
                    pressed=True,
                )
            )

        self._previous_pressed = current_pressed

        return events

    def release_all(self) -> list[G915XEvent]:
        """Generate a release event for the currently held G-key."""

        if self._previous_pressed is None:
            return []

        event = G915XEvent(
            key=self._previous_pressed,
            pressed=False,
        )

        self._previous_pressed = None

        return [event]

    def reset(self) -> None:
        """Reset the parser without generating release events."""

        self._previous_pressed = None
