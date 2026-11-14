
import os
from pathlib import Path

LOGITECH_VENDOR_ID = "046D"
LIGHTSPEED_RECEIVER_PID = "C547"

G915_X_WPID = "40B5"

HIDRAW_PATH = Path("/sys/class/hidraw")


class HidrawDevice:
    """Represents an opened Logitech HIDRAW device."""

    def __init__(self, path: str, fd: int):
        self.path = path
        self.fd = fd

    def close(self) -> None:
        if self.fd < 0:
            return

        os.close(self.fd)
        self.fd = -1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def _get_device_info(hidraw_path: Path) -> dict | None:
    """Read HID device metadata from sysfs."""

    device_path = hidraw_path / "device"

    try:
        resolved_path = device_path.resolve(strict=True)
    except OSError:
        return None

    current_path = resolved_path

    while current_path != current_path.parent:
        uevent_path = current_path / "uevent"

        if uevent_path.exists():
            try:
                content = uevent_path.read_text(
                    encoding="utf-8"
                )
            except OSError:
                content = ""

            info = {}

            for line in content.splitlines():
                if "=" not in line:
                    continue

                key, value = line.split("=", 1)
                info[key] = value

            if "HID_ID" in info:
                return info

        current_path = current_path.parent

    return None


def find_g915_x() -> str | None:
    """Find the G915 X Lightspeed keyboard HIDRAW node."""

    if not HIDRAW_PATH.exists():
        print("HIDRAW sysfs directory not found.")
        return None

    for hidraw_path in sorted(HIDRAW_PATH.glob("hidraw*")):
        info = _get_device_info(hidraw_path)

        if info is None:
            continue

        hid_id = info.get("HID_ID", "").split(":")

        if len(hid_id) != 3:
            continue

        _, vendor_id, product_id = hid_id

        if vendor_id.upper() != LOGITECH_VENDOR_ID:
            continue

        if product_id.upper() != LIGHTSPEED_RECEIVER_PID:
            continue

        modalias = info.get("MODALIAS", "")

        if G915_X_WPID not in modalias.upper():
            continue

        device_path = f"/dev/{hidraw_path.name}"

        print(f"Found Logitech G915 X: {device_path}")

        return device_path

    print("Logitech G915 X HIDRAW device not found.")
    return None


def open_g915_x() -> HidrawDevice:
    """Find and open the G915 X HIDRAW device."""

    device_path = find_g915_x()

    if device_path is None:
        raise RuntimeError(
            "Could not find Logitech G915 X HIDRAW device."
        )

    try:
        fd = os.open(
            device_path,
            os.O_RDONLY | os.O_NONBLOCK,
        )
    except OSError as error:
        raise RuntimeError(
            f"Could not open {device_path}: {error}"
        ) from error

    print(f"Opened G915 X HIDRAW device: {device_path}")

    return HidrawDevice(
        path=device_path,
        fd=fd,
    )
