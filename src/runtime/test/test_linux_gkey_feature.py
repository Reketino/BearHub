
import os
import time

RECEIVERS = [
    "/dev/hidraw3",
    "/dev/hidraw7",
]

DEVICE_IDS = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0xFF]

REPORT_ID = 0x11
ROOT_FEATURE_INDEX = 0x00
GET_FEATURE_FUNCTION = 0x00
GKEY_FEATURE_ID = 0x8010


def build_request(device_id: int) -> bytes:
    report = bytearray(20)

    report[0] = REPORT_ID
    report[1] = device_id
    report[2] = ROOT_FEATURE_INDEX
    report[3] = GET_FEATURE_FUNCTION
    report[4] = (GKEY_FEATURE_ID >> 8) & 0xFF
    report[5] = GKEY_FEATURE_ID & 0xFF

    return bytes(report)


def test_device(path: str, device_id: int) -> None:
    fd = os.open(path, os.O_RDWR | os.O_NONBLOCK)

    try:
        request = build_request(device_id)

        # Tøm eventuelle gamle rapporter.
        while True:
            try:
                if not os.read(fd, 64):
                    break
            except BlockingIOError:
                break

        os.write(fd, request)

        deadline = time.monotonic() + 1.0

        while time.monotonic() < deadline:
            try:
                response = os.read(fd, 64)
            except BlockingIOError:
                time.sleep(0.01)
                continue

            if not response:
                continue

            if response[0] != REPORT_ID:
                continue

            if response[1] != device_id:
                continue

            if response[2] != ROOT_FEATURE_INDEX:
                continue

            if response[3] != GET_FEATURE_FUNCTION:
                continue

            feature_index = response[4]
            feature_type = response[5]
            feature_version = response[6]

            if feature_index:
                print(
                    f"  FOUND: device={device_id:#04x}, "
                    f"index={feature_index:#04x}, "
                    f"type={feature_type:#04x}, "
                    f"version={feature_version}"
                )
            else:
                print(f"  Not available on device {device_id:#04x}")

            return

        print(f"  Timeout: device {device_id:#04x}")

    except OSError as error:
        print(f"  Error on device {device_id:#04x}: {error}")

    finally:
        os.close(fd)


def main() -> None:
    for receiver in RECEIVERS:
        print(f"\nTesting receiver: {receiver}")

        for device_id in DEVICE_IDS:
            test_device(receiver, device_id)


if __name__ == "__main__":
    main()
