
import os
import time
from collections.abc import Callable

from runtime.linux.g915_parser import (
    G915XEvent,
    G915XParser,
)
from runtime.linux.hidraw_device import open_g915_x


class G915XCalibrator:
    """Interactively validate G1-G9 on the Logitech G915 X."""

    POLL_INTERVAL = 0.01
    READ_SIZE = 64

    KEYS = (
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6",
        "G7",
        "G8",
        "G9",
    )

    def __init__(self):
        self._parser = G915XParser()
        self._pressed_keys: set[str] = set()

    def calibrate(
        self,
        progress_callback: Callable[[str], None] | None = None,
    ) -> None:
        device = open_g915_x()

        try:
            print("\nG915 X calibration started.")

            self._wait_for_all_keys_released(device)

            for expected_key in self.KEYS:
                if progress_callback is not None:
                    progress_callback(expected_key)

                print(f"\nPress {expected_key}...")

                self._wait_for_key_press(
                    device,
                    expected_key,
                )

                print(f"{expected_key} detected correctly.")

                self._wait_for_key_release(
                    device,
                    expected_key,
                )

                print(f"{expected_key} released.")

            print("\nG915 X calibration completed.")

        finally:
            device.close()

    def _read_events(self, device) -> list[G915XEvent]:
        while True:
            try:
                report = os.read(
                    device.fd,
                    self.READ_SIZE,
                )

            except BlockingIOError:
                time.sleep(self.POLL_INTERVAL)
                continue

            except InterruptedError:
                continue

            if not report:
                time.sleep(self.POLL_INTERVAL)
                continue

            events = self._parser.parse_report(report)

            for event in events:
                if event.pressed:
                    self._pressed_keys.add(event.key)
                else:
                    self._pressed_keys.discard(event.key)

            return events

    def _wait_for_all_keys_released(self, device) -> None:
        print("Release all G-keys before calibration.")

        while self._pressed_keys:
            self._read_events(device)

    def _wait_for_key_press(
        self,
        device,
        expected_key: str,
    ) -> None:
        while True:
            events = self._read_events(device)

            for event in events:
                if not event.pressed:
                    continue

                if event.key == expected_key:
                    return

                print(
                    f"Expected {expected_key}, "
                    f"but detected {event.key}. Try again."
                )

    def _wait_for_key_release(
        self,
        device,
        expected_key: str,
    ) -> None:
        while expected_key in self._pressed_keys:
            self._read_events(device)
