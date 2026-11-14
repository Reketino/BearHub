
from runtime.linux.hidraw_device import find_g915_x, open_g915_x


def main():
    print("Searching for Logitech G915 X...\n")

    path = find_g915_x()

    if path is None:
        print("Device discovery failed.")
        return

    print(f"\nDiscovered device: {path}")

    print("\nTesting device access...")

    try:
        with open_g915_x() as device:
            print(f"Device path: {device.path}")
            print(f"File descriptor: {device.fd}")
            print("HIDRAW access successful.")

    except RuntimeError as error:
        print(f"Device test failed: {error}")


if __name__ == "__main__":
    main()
