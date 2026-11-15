import errno
import os
import threading
import traceback

from collections.abc import Callable
from enum import Enum, auto

from runtime.linux.g915_parser import (
    G915XEvent,
    G915XParser,
)
from runtime.linux.hidraw_device import (
    HidrawDeviceAccessError,
    HidrawDeviceNotFoundError,
    open_g915_x,
)


class ReaderState(Enum):
    """Lifecycle states for the HIDRAW reader."""

    STOPPED = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    DISCONNECTED = auto()
    FAILED = auto()


class HidrawReader:
    """Read Logitech G915 X HID reports in a background thread."""

    READ_SIZE = 64
    POLL_INTERVAL = 0.01

    DISCONNECT_ERRNOS = {
        errno.EIO,
        errno.ENODEV,
        errno.ENXIO,
        errno.ENOENT,
    }

    def __init__(
        self,
        on_event: Callable[[G915XEvent], None],
        on_error: Callable[[Exception], None] | None = None,
    ):
        self._on_event = on_event
        self._on_error = on_error

        self._parser = G915XParser()
        self._stop_event = threading.Event()
        self._lock = threading.RLock()

        self._thread: threading.Thread | None = None
        self._state = ReaderState.STOPPED
        self._last_error: Exception | None = None

    @property
    def state(self) -> ReaderState:
        """Return the current reader state."""

        with self._lock:
            return self._state

    @property
    def last_error(self) -> Exception | None:
        """Return the most recent reader error."""

        with self._lock:
            return self._last_error

    @property
    def is_running(self) -> bool:
        """Return whether the reader is actively running."""

        return self.state == ReaderState.RUNNING

    def start(self) -> None:
        """Start the HIDRAW reader."""

        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                raise RuntimeError(
                    "HIDRAW reader is already active."
                )

            self._stop_event.clear()
            self._parser.reset()
            self._last_error = None
            self._state = ReaderState.STARTING

            self._thread = threading.Thread(
                target=self._run,
                name="G915X-HIDRAW-Reader",
                daemon=False,
            )

            self._thread.start()

    def stop(self, timeout: float | None = 2.0) -> None:
        """Request shutdown and wait for the reader thread."""

        with self._lock:
            thread = self._thread

            if thread is None:
                if self._state not in (
                    ReaderState.FAILED,
                    ReaderState.DISCONNECTED,
                ):
                    self._state = ReaderState.STOPPED
                return

            if thread is threading.current_thread():
                raise RuntimeError(
                    "Reader cannot join its own thread."
                )

            self._stop_event.set()

            if thread.is_alive():
                self._state = ReaderState.STOPPING

        thread.join(timeout=timeout)

        if thread.is_alive():
            raise TimeoutError(
                "G915 X HIDRAW reader did not stop in time."
            )

        with self._lock:
            if self._thread is thread:
                self._thread = None

            if self._state == ReaderState.STOPPING:
                self._state = ReaderState.STOPPED

    def _run(self) -> None:
        """Open the device and process reports until stopped."""

        device = None

        try:
            if self._stop_event.is_set():
                return

            device = open_g915_x()

            with self._lock:
                if not self._stop_event.is_set():
                    self._state = ReaderState.RUNNING

            while not self._stop_event.is_set():
                try:
                    report = os.read(
                        device.fd,
                        self.READ_SIZE,
                    )

                except BlockingIOError:
                    self._stop_event.wait(self.POLL_INTERVAL)
                    continue

                except InterruptedError:
                    continue

                except OSError as error:
                    if self._stop_event.is_set():
                        break

                    if self._is_disconnected(error):
                        self._set_state(ReaderState.DISCONNECTED)
                    else:
                        self._set_state(ReaderState.FAILED)

                    self._report_error(error)
                    break

                if not report:
                    self._stop_event.wait(self.POLL_INTERVAL)
                    continue

                self._process_report(report)

        except HidrawDeviceNotFoundError as error:
            self._set_state(ReaderState.DISCONNECTED)
            self._report_error(error)

        except HidrawDeviceAccessError as error:
            self._set_state(ReaderState.FAILED)
            self._report_error(error)

        except Exception as error:
            self._set_state(ReaderState.FAILED)
            self._report_error(error)

        finally:
            self._release_held_keys()

            if device is not None:
                try:
                    device.close()
                except OSError as error:
                    self._set_state(ReaderState.FAILED)
                    self._report_error(error)

            with self._lock:
                if self._state == ReaderState.STOPPING:
                    self._state = ReaderState.STOPPED
                elif self._state == ReaderState.STARTING:
                    self._state = ReaderState.STOPPED

    @classmethod
    def _is_disconnected(cls, error: OSError) -> bool:
        """Check whether an OS error indicates device removal."""

        return error.errno in cls.DISCONNECT_ERRNOS

    def _set_state(self, state: ReaderState) -> None:
        """Update reader state safely."""

        with self._lock:
            self._state = state

    def _process_report(self, report: bytes) -> None:
        """Parse a report and dispatch its events."""

        for event in self._parser.parse_report(report):
            self._dispatch_event(event)

    def _release_held_keys(self) -> None:
        """Dispatch release events for held G-keys."""

        for event in self._parser.release_all():
            self._dispatch_event(event)

    def _dispatch_event(self, event: G915XEvent) -> None:
        """Send an event to the registered callback."""

        try:
            self._on_event(event)
        except Exception as error:
            self._report_error(error)

    def _report_error(self, error: Exception) -> None:
        """Store and forward reader errors."""

        with self._lock:
            self._last_error = error

        if self._on_error is None:
            traceback.print_exception(error)
            return

        try:
            self._on_error(error)
        except Exception:
            traceback.print_exc()
