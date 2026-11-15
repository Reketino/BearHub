import time

from runtime.linux_macro_listener import LinuxMacroListener


def main():
    listener = LinuxMacroListener()

    listener.set_callback(
        lambda key: print(f"MACRO TRIGGERED: {key}")
    )

    print("Starting LinuxMacroListener...")
    print("Press G1-G9 to test.")
    print("Unplug/reconnect the receiver to test recovery.")
    print("Press Ctrl+C to stop.")

    try:
        listener.start()

        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopping listener...")

    finally:
        listener.stop()


if __name__ == "__main__":
    main()