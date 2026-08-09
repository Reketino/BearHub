import os
import struct
from threading import Thread


LINUX_INPUT_DEVICE = "/dev/input/event3"

EV_KEY = 1

G_KEY_MAP = {
    183: "G1",  # F13
    184: "G2",  # F14
    185: "G3",  # F15
    186: "G4",  # F16
    187: "G5",  # F17
    188: "G6",  # F18
    189: "G7",  # F19
    190: "G8",  # F20
    191: "G9",  # F21
}


class LinuxMacroListener:
    def __init__(self, device_path=LINUX_INPUT_DEVICE):
        self.device_path = device_path
        self.running = False
        self.thread = None
        self.callback = None

    def set_callback(self, callback):
        self.callback = callback

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
        try:
            with open(self.device_path, "rb") as device:
                print(
                    f"Listening for G-keys on "
                    f"{self.device_path}"
                )

                while self.running:
                    event = device.read(24)

                    if len(event) != 24:
                        continue

                    _, _, event_type, code, value = struct.unpack(
                        "llHHI",
                        event,
                    )

                    if event_type != EV_KEY:
                        continue

                    if value != 1:
                        continue

                    g_key = G_KEY_MAP.get(code)

                    if g_key is None:
                        continue

                    print(f"Pressed {g_key}")

                    if self.callback:
                        self.callback(g_key)

        except PermissionError:
            print(
                f"Permission denied: {self.device_path}"
            )
            print(
                "Run the test with sudo or configure "
                "udev permissions."
            )

        except FileNotFoundError:
            print(
                f"Input device not found: "
                f"{self.device_path}"
            )

        except Exception as error:
            if self.running:
                print(
                    f"Linux input error: {error}"
                )

        finally:
            self.running = False
            print("Linux G-key listener stopped.")

    def stop(self):
        if not self.running:
            return

        self.running = False

        if (
            self.thread is not None
            and self.thread.is_alive()
        ):
            self.thread.join(timeout=1)

        self.thread = None