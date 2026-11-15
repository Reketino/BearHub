from collections.abc import Callable

from runtime.linux.g915_parser import G915XEvent
from runtime.linux.reconnect_manager import ReconnectManager


class LinuxMacroListener:
    """Connects Linux HIDRAW G-key events to the macro engine."""

    def __init__(self):
        self._callback: Callable[[str], None] | None = None
        self._manager: ReconnectManager | None = None

    def set_callback(self, callback: Callable[[str], None]) -> None:
        self._callback = callback

    def start(self) -> None:
        if self._manager is not None and self._manager.is_running:
            return

        self._manager = ReconnectManager(
            on_event=self._handle_event,
            on_error=self._handle_error,
        )

        self._manager.start()

        print("Linux G-key listener started.")
        print("Listening for G1-G9.")

    def stop(self) -> None:
        if self._manager is None:
            return

        try:
            self._manager.stop()
        except TimeoutError as error:
            print(f"Linux G-key listener shutdown error: {error}")
            raise

        self._manager = None

        print("Linux G-key listener stopped.")

    def _handle_event(self, event: G915XEvent) -> None:
        if not event.pressed:
            return

        print(f"Pressed {event.key}")

        if self._callback is not None:
            self._callback(event.key)

    @staticmethod
    def _handle_error(error: Exception) -> None:
        print(f"Linux G-key listener: {error}")
