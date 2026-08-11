import keyboard
from threading import Thread

import keyboard
from threading import Thread


F_KEY_TO_G_KEY = {
    "f15": "G1",
    "f16": "G2",
    "f17": "G3",
    "f18": "G4",
    "f19": "G5",
    "f20": "G6",
    "f21": "G7",
    "f22": "G8",
    "f23": "G9",
}


class WindowsMacroListener:
    def __init__(self):
        self.running = False
        self.callback = None
        self.hooks = []

    def set_callback(self, callback):
        self.callback = callback

    def start(self):
        if self.running:
            return

        self.running = True

        for key, g_key in F_KEY_TO_G_KEY.items():
            hook = keyboard.on_press_key(
                key,
                lambda event, g_key=g_key: self._handle_key(g_key),
            )

            self.hooks.append(hook)

        print("Windows G-key listener started.")
        print("Listening for G1-G9.")

    def _handle_key(self, g_key):
        if not self.running:
            return

        print(f"Pressed {g_key}")

        if self.callback:
            self.callback(g_key)

    def stop(self):
        if not self.running:
            return

        self.running = False

        for hook in self.hooks:
            keyboard.unhook(hook)

        self.hooks.clear()

        print("Windows G-key listener stopped.")