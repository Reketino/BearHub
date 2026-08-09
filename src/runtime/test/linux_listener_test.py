import time

from src.runtime.linux_macro_listener import LinuxMacroListener


def on_key_pressed(key):
    print(f"CALLBACK: {key}")


listener = LinuxMacroListener()

listener.set_callback(
    on_key_pressed
)

listener.start()

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    listener.stop()