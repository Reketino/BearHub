
import time

from runtime.linux.g915_parser import G915XEvent
from runtime.linux.reconnect_manager import (
    ReconnectManager,
    ReconnectState,
)


def handle_event(event: G915XEvent) -> None:
    action = "PRESSED" if event.pressed else "RELEASED"
    print(f"{event.key}: {action}")


def handle_error(error: Exception) -> None:
    print(f"RECONNECT ERROR: {error}")


def main() -> None:
    manager = ReconnectManager(
        on_event=handle_event,
        on_error=handle_error,
        retry_interval=2.0,
    )

    print("Starting BearHub reconnect manager...")
    print("Connect your G915 X receiver.")
    print("Unplug and reconnect it to test recovery.")
    print("Press Ctrl+C to stop.\n")

    try:
        manager.start()

        while manager.is_running:
            state = manager.state

            print(
                f"\rManager state: {state.name}   ",
                end="",
                flush=True,
            )

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\nTest interrupted.")

    finally:
        print("\nStopping reconnect manager...")

        try:
            manager.stop()
        except TimeoutError as error:
            print(f"Shutdown error: {error}")

        print(f"Final state: {manager.state.name}")
        print("Test finished.")


if __name__ == "__main__":
    main()
