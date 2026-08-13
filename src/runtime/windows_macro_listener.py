import time
from threading import Thread

from runtime.hid_device import find_device
from runtime.hid_parser import parse_report


class WindowsMacroListener:

    def __init__(self):
        self.callback = None
        self.running = False
        self.hook = None

    def set_callback(self, callback):
        self.callback = callback

    def start(self):
        if self.running:
            return

        self.running = True

        self.hook = keyboard.hook(
            self._on_key_event
        )

        print("Windows G-key listener started.")
        print("Listening for G1-G9.")

    def stop(self):
        if not self.running:
            return

        self.running = False

        if self.hook is not None:
            keyboard.unhook(self.hook)
            self.hook = None

        print("Windows G-key listener stopped.")