import hid
import threading
import time


VENDOR_ID = 0x046D
PRODUCT_ID = 0xC547

USAGE_PAGE = 65280
USAGE = 2


devices = []

for device in hid.enumerate():
    if (
        device["vendor_id"] == VENDOR_ID
        and device["product_id"] == PRODUCT_ID
        and device.get("usage_page") == USAGE_PAGE
        and device.get("usage") == USAGE
    ):
        devices.append(device)


print(
    f"Found {len(devices)} G-key interfaces.\n"
)


running = True


def listen_device(index, device):
    global running

    hid_device = hid.device()

    print("=" * 60)
    print(f"DEVICE {index}")
    print(f"Interface : {device.get('interface_number')}")
    print(f"Usage     : {device.get('usage')}")
    print(f"Path      : {device['path']}")

    try:
        hid_device.open_path(device["path"])

        print("Opened.")
        print("Listening...\n")

        hid_device.set_nonblocking(True)

        while running:
            reports = hid_device.read(64)

            for report in reports:
                print(
                    f"[DEVICE {index}] "
                    f"{report}"
                )

            time.sleep(0.01)

    except Exception as error:
        print(
            f"[DEVICE {index}] ERROR: {error}"
        )

    finally:
        try:
            hid_device.close()
        except Exception:
            pass

        print(
            f"[DEVICE {index}] Closed."
        )


threads = []

for index, device in enumerate(devices):
    thread = threading.Thread(
        target=listen_device,
        args=(index, device),
        daemon=True,
    )

    thread.start()
    threads.append(thread)


print("=" * 60)
print("G-KEY INTERFACES ARE LISTENING")
print("=" * 60)
print()
print("Press G2 once.")
print("Then wait 3 seconds.")
print("Press Ctrl+C to stop.")
print()


try:
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopping...")

    running = False

    for thread in threads:
        thread.join(timeout=1)

    print("Done.")