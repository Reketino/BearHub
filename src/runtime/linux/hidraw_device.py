
import os
from pathlib import Path


LOGITECH_VENDOR_ID = 0x046D
G915_X_WPID = 0x40B5

HIDRAW_PATH = Path("/sys/class/hidraw")


class HidrawDeviceNotFoundError(RuntimeError):
    """Raised when the G915 X device cannot be found."""


class HidrawDeviceAccessError(RuntimeError):
    """Raised when the G915 X device cannot be opened."""


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
                content = uevent_path.read_text(encoding="utf-8")
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
        return None

    for hidraw_path in sorted(HIDRAW_PATH.glob("hidraw*")):
        info = _get_device_info(hidraw_path)

        if info is None:
            continue

        hid_id = info.get("HID_ID", "").split(":")

        if len(hid_id) != 3:
            continue

        try:
            _, vendor_id, product_id = (
                int(value, 16) for value in hid_id
            )
        except ValueError:
            continue

        if vendor_id != LOGITECH_VENDOR_ID:
            continue

        if product_id != G915_X_WPID:
            continue

        if info.get("HID_NAME") != "Logitech G915 X":
            continue

        return f"/dev/{hidraw_path.name}"

    return None


def open_g915_x() -> HidrawDevice:
    """Find and open the G915 X HIDRAW device."""

    device_path = find_g915_x()

    if device_path is None:
        raise HidrawDeviceNotFoundError(
            "Logitech G915 X HIDRAW device not found."
        )

    try:
        fd = os.open(
            device_path,
            os.O_RDONLY | os.O_NONBLOCK,
        )
    except OSError as error:
        raise HidrawDeviceAccessError(
            f"Could not open {device_path}: {error}"
        ) from error

    print(f"Opened Logitech G915 X: {device_path}")

    return HidrawDevice(
        path=device_path,
        fd=fd,
    )
