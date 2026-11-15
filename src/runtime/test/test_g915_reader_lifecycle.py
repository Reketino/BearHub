
import unittest

from unittest.mock import patch

from runtime.linux.hidraw_reader import (
    HidrawReader,
    ReaderState,
)


class FakeHidrawDevice:
    """Simulated HIDRAW device for lifecycle tests."""

    fd = 123

    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class TestHidrawReaderLifecycle(unittest.TestCase):

    def setUp(self):
        self.device = FakeHidrawDevice()
        self.events = []
        self.errors = []

        self.open_patcher = patch(
            "runtime.linux.hidraw_reader.open_g915_x",
            return_value=self.device,
        )

        self.open_device = self.open_patcher.start()
        self.addCleanup(self.open_patcher.stop)

        self.read_patcher = patch(
            "runtime.linux.hidraw_reader.os.read",
            side_effect=BlockingIOError,
        )

        self.read_patcher.start()
        self.addCleanup(self.read_patcher.stop)

    def create_reader(self):
        return HidrawReader(
            on_event=self.events.append,
            on_error=self.errors.append,
        )

    def test_reader_starts_and_stops(self):
        reader = self.create_reader()

        reader.start()
        reader.stop()

        self.assertEqual(reader.state, ReaderState.STOPPED)
        self.assertFalse(reader.is_running)
        self.assertTrue(self.device.closed)

    def test_start_twice_raises_error(self):
        reader = self.create_reader()

        reader.start()

        try:
            with self.assertRaises(RuntimeError):
                reader.start()
        finally:
            reader.stop()

    def test_stop_can_be_called_multiple_times(self):
        reader = self.create_reader()

        reader.start()
        reader.stop()
        reader.stop()

        self.assertEqual(reader.state, ReaderState.STOPPED)

    def test_device_open_failure_sets_failed_state(self):
        error = OSError("Device unavailable")

        self.open_device.side_effect = error

        reader = self.create_reader()
        reader.start()

        thread = reader._thread
        thread.join(timeout=2)

        self.assertFalse(thread.is_alive())
        self.assertEqual(reader.state, ReaderState.FAILED)
        self.assertIn(error, self.errors)

        reader.stop()

        self.assertEqual(reader.state, ReaderState.FAILED)

    def test_reader_can_restart_after_normal_stop(self):
        reader = self.create_reader()

        reader.start()
        reader.stop()

        reader.start()
        reader.stop()

        self.assertEqual(reader.state, ReaderState.STOPPED)
        self.assertEqual(self.open_device.call_count, 2)

    def test_eio_is_classified_as_disconnection(self):
        reader = self.create_reader()

        error = OSError(5, "Input/output error")

        self.assertTrue(
            reader._is_disconnected(error)
    )

    
def test_eio_sets_disconnected_state(self):
    error = OSError(5, "Input/output error")

    self.open_device.return_value = self.device

    with patch(
        "runtime.linux.hidraw_reader.os.read",
        side_effect=error,
    ):
        reader = self.create_reader()
        reader.start()

        thread = reader._thread
        thread.join(timeout=2)

    self.assertFalse(thread.is_alive())
    self.assertEqual(
        reader.state,
        ReaderState.DISCONNECTED,
    )
    self.assertIn(error, self.errors)
    self.assertTrue(self.device.closed)

def test_eio_sets_disconnected_state(self):
    error = OSError(5, "Input/output error")

    self.open_device.return_value = self.device

    with patch(
        "runtime.linux.hidraw_reader.os.read",
        side_effect=error,
    ):
        reader = self.create_reader()
        reader.start()

        thread = reader._thread
        thread.join(timeout=2)

    self.assertFalse(thread.is_alive())
    self.assertEqual(
        reader.state,
        ReaderState.DISCONNECTED,
    )
    self.assertIn(error, self.errors)
    self.assertTrue(self.device.closed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
