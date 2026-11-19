
import time

from runtime.linux.keyboard_listener import KeyboardListener


def on_key_pressed(key: str) -> None:
    print(f"Detected trigger: {key}")


listener = KeyboardListener(
    on_key_pressed=on_key_pressed,
    triggers={
        "a": True,
    },
)

try:
    listener.start()

    print("\nKeyboard listener is running.")
    print("Open a text editor and press A.")
    print("A should NOT appear in the text editor.")
    print("Press Ctrl+C here to stop.\n")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping listener...")

finally:
    listener.stop()
