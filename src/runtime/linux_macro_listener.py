from select import select
from threading import Thread

from evdev import InputDevice, ecodes, list_devices

LOGITECH_VENDOR_ID = 0x046D
LOGITECH_PRODUCT_ID = 0xC547

G_KEY_CODES = {
    ecodes.KEY_F15: "G2",
    ecodes.KEY_F16: "G3",
    ecodes.KEY_F17: "G4",
    ecodes.KEY_F18: "G5",
    ecodes.KEY_F19: "G6",
    ecodes.KEY_F20: "G7",
    ecodes.KEY_F21: "G8",
    ecodes.KEY_F22: "G9",
}

class LinuxMacroListener:
    def __init__(self):
        self.running = False
        self.callback = None
        self.thread = None
        self.devices = []

    def set_callback(self, callback):
        self.callback = callback

    def find_devices(self):
        devices = []

        for path in list_devices():
            try:
                device = InputDevice(path)
            except Exception:
                continue

            if device.info.vendor != LOGITECH_VENDOR_ID:
                device.close()
                continue

            if device.info.product != LOGITECH_PRODUCT_ID:
                device.close()
                continue

            if "Keyboard" not in device.name:
                device.close()
                continue

            devices.append(device)

        return devices

    def start(self):
        if self.running:
            return

        self.running = True

        self.thread = Thread(
            target=self.listen,
            daemon=True,
        )

        self.thread.start()

        print("Linux G-key listener started.")

    def listen(self):
        devices = self.find_devices()

        if not devices:
            print(
                "No Logitech USB Receiver Keyboard found."
            )

            self.running = False
            return

        self.devices = devices

        for device in self.devices:
            print(
                f"Listening for G-keys on "
                f"{device.path} - {device.name}"
            )

        try:
            while self.running:
                readable, _, _ = select(
                    self.devices,
                    [],
                    [],
                    0.5,
                )

                for device in readable:
                    try:
                        events = device.read()

                    except OSError as error:
                        if self.running:
                            print(
                                f"Input error on "
                                f"{device.path}: {error}"
                            )

                        continue

                    for event in events:
                        self.handle_event(event)

        finally:
            self.close_devices()

    def handle_event(self, event):
        if event.type != ecodes.EV_KEY:
            return

        if event.value != 1:
            return

        key = G_KEY_CODES.get(event.code)

        if key is None:
            return

        print(f"Pressed {key}")

        if self.callback:
            self.callback(key)

    def stop(self):
        if not self.running:
            return

        self.running = False

        if (
            self.thread is not None
            and self.thread.is_alive()
        ):
            self.thread.join(timeout=1)

        self.close_devices()

        self.thread = None

        print("Linux G-key listener stopped.")

    def close_devices(self):
        for device in self.devices:
            try:
                device.close()
            except Exception:
                pass

        self.devices = []