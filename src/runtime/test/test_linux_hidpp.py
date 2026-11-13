
import os
import select
import time

DEVICE_PATH = "/dev/hidraw3"

HIDPP_LONG_REPORT_ID = 0x11
HIDPP_DEVICE_ID = 0x01

# HID++ feature-index lookup request.
# Feature index 0, function 0, feature ID 0x0000.
request = bytearray(20)
request[0] = HIDPP_LONG_REPORT_ID
request[1] = HIDPP_DEVICE_ID
request[2] = 0x00
request[3] = 0x00

fd = None

try:
    fd = os.open(DEVICE_PATH, os.O_RDWR | os.O_NONBLOCK)

    print(f"Opened: {DEVICE_PATH}")

    written = os.write(fd, request)
    print(f"Bytes written: {written}")

    ready, _, _ = select.select([fd], [], [], 2.0)

    if not ready:
        print("No HID++ response received.")
    else:
        response = os.read(fd, 64)
        print("HID++ response:", list(response))

except OSError as error:
    print(f"HIDRAW error: {error}")

finally:
    if fd is not None:
        os.close(fd)
        print("Device closed.")
