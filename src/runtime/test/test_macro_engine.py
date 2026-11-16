
import time

from models.macro import Macro
from runtime.macro_engine import MacroEngine


def main() -> None:
    engine = MacroEngine()

    test_macro = Macro(
        id="test-001",
        name="Linux G1 test",
        value="BearHub fungerer!",
        macro_type="text",
        input_id="399",
    )

    engine.load_profile([test_macro])

    print("\nStarting MacroEngine...")
    print("Press G1 to execute the test macro.")
    print("Press Ctrl+C to stop.\n")

    try:
        engine.start()

        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopping MacroEngine...")

    finally:
        engine.stop()


if __name__ == "__main__":
    main()
