
import threading
import time
import unittest

from unittest.mock import patch

from runtime.linux.hidraw_reader import ReaderState
from runtime.linux.reconnect_manager import (
    ReconnectManager,
    ReconnectState,
)


class FakeReader:
    """Simulated reader for reconnect tests."""

    def __init__(self, state):
        self.state = state
        self.last_error = None
        self.stopped = False

    def start(self):
        pass

    def stop(self):
        self.stopped = True


class TestReconnectManager(unittest.TestCase):

    def setUp(self):
        self.events = []
        self.errors = []

    def create_manager(self, retry_interval=0.02):
        return ReconnectManager(
            on_event=self.events.append,
            on_error=self.errors.append,
            retry_interval=retry_interval,
        )

    def test_invalid_retry_interval_raises_error(self):
        with self.assertRaises(ValueError):
            self.create_manager(retry_interval=0)

    def test_manager_starts_and_stops(self):
        manager = self.create_manager()

        fake_reader = FakeReader(ReaderState.RUNNING)

        with patch.object(
            manager,
            "_create_reader",
            return_value=fake_reader,
        ):
            manager.start()

            deadline = time.monotonic() + 2

            while manager.state != ReconnectState.RUNNING:
                if time.monotonic() > deadline:
                    self.fail("Manager did not reach RUNNING state")

                time.sleep(0.01)

            manager.stop()

        self.assertEqual(manager.state, ReconnectState.STOPPED)
        self.assertFalse(manager.is_running)
        self.assertTrue(fake_reader.stopped)

    def test_manager_reconnects_after_disconnection(self):
        second_reader_started = threading.Event()

        readers = [
            FakeReader(ReaderState.DISCONNECTED),
            FakeReader(ReaderState.RUNNING),
        ]

        def create_fake_reader():
            reader = readers.pop(0)

            if not readers:
                original_start = reader.start

                def start():
                    original_start()
                    second_reader_started.set()

                reader.start = start

            return reader

        manager = self.create_manager()

        with patch.object(
            manager,
            "_create_reader",
            side_effect=create_fake_reader,
        ) as create_reader:
            manager.start()

            self.assertTrue(
                second_reader_started.wait(timeout=2),
                "Manager did not create a replacement reader.",
            )

            manager.stop()

        self.assertGreaterEqual(create_reader.call_count, 2)
        self.assertEqual(manager.state, ReconnectState.STOPPED)

    def test_manager_stops_during_retry_wait(self):
        fake_reader = FakeReader(ReaderState.DISCONNECTED)
        manager = self.create_manager(retry_interval=10)

        with patch.object(
            manager,
            "_create_reader",
            return_value=fake_reader,
        ):
            manager.start()

            deadline = time.monotonic() + 2

            while manager.state != ReconnectState.RECONNECTING:
                if time.monotonic() > deadline:
                    self.fail("Manager did not enter reconnecting state")

                time.sleep(0.01)

            started_at = time.monotonic()
            manager.stop(timeout=2)
            elapsed = time.monotonic() - started_at

        self.assertLess(elapsed, 2)
        self.assertEqual(manager.state, ReconnectState.STOPPED)


if __name__ == "__main__":
    unittest.main(verbosity=2)
