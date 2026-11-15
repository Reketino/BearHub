
import threading
import traceback

from collections.abc import Callable
from enum import Enum, auto

from runtime.linux.g915_parser import G915XEvent
from runtime.linux.hidraw_reader import (
    HidrawReader,
    ReaderState,
)


class ReconnectState(Enum):
    """Lifecycle states for the reconnect manager."""

    STOPPED = auto()
    STARTING = auto()
    RUNNING = auto()
    RECONNECTING = auto()
    STOPPING = auto()
    FAILED = auto()


class ReconnectManager:
    """Manage HIDRAW reader lifecycle and automatic reconnection."""

    MONITOR_INTERVAL = 0.05

    def __init__(
        self,
        on_event: Callable[[G915XEvent], None],
        on_error: Callable[[Exception], None] | None = None,
        retry_interval: float = 2.0,
    ):
        if retry_interval <= 0:
            raise ValueError("Retry interval must be greater than zero.")

        self._on_event = on_event
        self._on_error = on_error
        self._retry_interval = retry_interval

        self._stop_event = threading.Event()
        self._lock = threading.RLock()

        self._thread: threading.Thread | None = None
        self._reader: HidrawReader | None = None

        self._state = ReconnectState.STOPPED
        self._last_error: Exception | None = None

    @property
    def state(self) -> ReconnectState:
        """Return the current manager state."""

        with self._lock:
            return self._state

    @property
    def last_error(self) -> Exception | None:
        """Return the most recent error."""

        with self._lock:
            return self._last_error

    @property
    def is_running(self) -> bool:
        """Return whether the manager thread is active."""

        with self._lock:
            return (
                self._thread is not None
                and self._thread.is_alive()
            )

    def start(self) -> None:
        """Start managing the HIDRAW reader."""

        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                raise RuntimeError(
                    "Reconnect manager is already active."
                )

            self._stop_event.clear()
            self._last_error = None
            self._state = ReconnectState.STARTING

            self._thread = threading.Thread(
                target=self._run,
                name="G915X-Reconnect-Manager",
                daemon=False,
            )

            self._thread.start()

    def stop(self, timeout: float | None = 5.0) -> None:
        """Stop reconnect attempts and shut down the active reader."""

        with self._lock:
            thread = self._thread

            if thread is None:
                if self._state != ReconnectState.FAILED:
                    self._state = ReconnectState.STOPPED
                return

            if thread is threading.current_thread():
                raise RuntimeError(
                    "Reconnect manager cannot join its own thread."
                )

            self._state = ReconnectState.STOPPING
            self._stop_event.set()

        thread.join(timeout=timeout)

        if thread.is_alive():
            raise TimeoutError(
                "Reconnect manager did not stop in time."
            )

        with self._lock:
            if self._thread is thread:
                self._thread = None

            self._reader = None

            if self._state == ReconnectState.STOPPING:
                self._state = ReconnectState.STOPPED

    def _run(self) -> None:
        """Manage reader instances until stopped or failed."""

        try:
            while not self._stop_event.is_set():
                reader = self._create_reader()

                with self._lock:
                    self._reader = reader

                reader.start()

                result = self._monitor_reader(reader)

                try:
                    reader.stop()
                except TimeoutError as error:
                    self._set_failed(error)
                    self._report_error(error)
                    return

                if self._stop_event.is_set():
                    break

                if result == ReaderState.DISCONNECTED:
                    self._set_state(ReconnectState.RECONNECTING)

                    if self._stop_event.wait(self._retry_interval):
                        break

                    continue

                if result == ReaderState.FAILED:
                    error = reader.last_error or RuntimeError(
                        "HIDRAW reader failed without an error."
                    )

                    self._set_failed(error)
                    self._report_error(error)
                    return

                error = RuntimeError(
                    f"Unexpected HIDRAW reader state: {result.name}"
                )

                self._set_failed(error)
                self._report_error(error)
                return

        except Exception as error:
            self._set_failed(error)
            self._report_error(error)

        finally:
            with self._lock:
                reader = self._reader

            if reader is not None:
                try:
                    reader.stop()
                except Exception as error:
                    self._report_error(error)

            with self._lock:
                self._reader = None

                if self._state == ReconnectState.STOPPING:
                    self._state = ReconnectState.STOPPED
                elif self._state == ReconnectState.STARTING:
                    self._state = ReconnectState.STOPPED

    def _create_reader(self) -> HidrawReader:
        """Create a new HIDRAW reader."""

        return HidrawReader(
            on_event=self._on_event,
            on_error=self._report_error,
        )

    def _monitor_reader(
        self,
        reader: HidrawReader,
    ) -> ReaderState:
        """Monitor a reader until it reaches a terminal state."""

        while not self._stop_event.is_set():
            state = reader.state

            if state == ReaderState.RUNNING:
                self._set_state(ReconnectState.RUNNING)

            elif state in (
                ReaderState.DISCONNECTED,
                ReaderState.FAILED,
                ReaderState.STOPPED,
            ):
                return state

            self._stop_event.wait(self.MONITOR_INTERVAL)

        return ReaderState.STOPPED

    def _set_state(self, state: ReconnectState) -> None:
        """Update manager state safely."""

        with self._lock:
            self._state = state

    def _set_failed(self, error: Exception) -> None:
        """Store an error and mark the manager as failed."""

        with self._lock:
            self._last_error = error
            self._state = ReconnectState.FAILED

    def _report_error(self, error: Exception) -> None:
        """Forward errors to the registered callback."""

        with self._lock:
            self._last_error = error

        if self._on_error is None:
            traceback.print_exception(error)
            return

        try:
            self._on_error(error)
        except Exception:
            traceback.print_exc()
