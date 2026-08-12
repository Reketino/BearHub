import keyboard


class WindowsMacroListener:
    KEY_TO_G_KEY = {
        "f13": "G1",
        "f14": "G2",
        "f15": "G3",
        "f16": "G4",
        "f17": "G5",
        "f18": "G6",
        "f19": "G7",
        "f20": "G8",
        "f21": "G9",
    }

    def __init__(self):
        self.callback = None
        self.running = False
        self.hook = None

    def set_callback(self, callback):
        self.callback = callback

    def _on_key_event(self, event):
        if not self.running:
            return
        
        print(
            f"Keyboard event: "
            f"type={event.event_type} "
            f"key={event.name} "
            f"scan_code={event.scan_code}"
        )

        if event.event_type != "down":
            return

        key = event.name.lower()

        g_key = self.KEY_TO_G_KEY.get(key)

        if g_key is None:
            return

        print(f"Pressed {g_key}")

        if self.callback is not None:
            self.callback(g_key)

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