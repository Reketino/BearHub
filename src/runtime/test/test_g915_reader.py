
import errno
import time

from runtime.linux.g915_parser import G915XEvent
from runtime.linux.hidraw_reader import (
    HidrawReader,
    ReaderState,
)


def handle_event(event: G915XEvent) -> None:
    action = "PRESSED" if event.pressed else "RELEASED"
    print(f"{event.key}: {action}")


def handle_error(error: Exception) -> None:
    error_number = getattr(error, "errno", None)

    if error_number is not None:
        error_name = errno.errorcode.get(
            error_number,
            "UNKNOWN",
        )

        print(
            f"HIDRAW ERROR: {error_name} "
            f"({error_number}): {error}"
        )
    else:
        print(f"HIDRAW ERROR: {error}")


def main() -> None:
    reader = HidrawReader(
        on_event=handle_event,
        on_error=handle_error,
    )

    print("Starting G915 X HIDRAW reader...")
    print("Unplug the G915 X receiver to test disconnection.")
    print("Press Ctrl+C to stop.\n")

    try:
        reader.start()

        while reader.is_running or reader.state == ReaderState.STARTING:
            time.sleep(0.1)

        print(f"\nReader state: {reader.state.name}")

        if reader.last_error:
            print(f"Last error: {reader.last_error}")

    except KeyboardInterrupt:
        print("\nTest interrupted by user.")

    finally:
        print("\nStopping HIDRAW reader...")

        try:
            reader.stop()
        except TimeoutError as error:
            print(f"Shutdown error: {error}")

        print(f"Final state: {reader.state.name}")
        print("HIDRAW reader stopped.")


if __name__ == "__main__":
    main()
