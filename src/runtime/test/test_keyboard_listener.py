
import time

from runtime.linux.keyboard_listener import KeyboardListener


def on_key_pressed(key: str) -> None:
    print(f"Detected keyboard trigger: {key}")


triggers = {
    "a": True,
    "Return": False,
    "F1": True,
}

listener = KeyboardListener(
    on_key_pressed=on_key_pressed,
    triggers=triggers,
)

try:
    listener.start()

    print("Press A, Enter or F1.")
    print("Press Ctrl+C to stop.")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping listener...")

finally:
    listener.stop()
