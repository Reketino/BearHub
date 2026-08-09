import hid
from threading import Thread


PATHS = [
    b"1-4:1.2",
    b"1-9.1:1.2",
]


def listen(path, index):
    device = hid.device()

    try:
        device.open_path(path)
        device.set_nonblocking(True)

        print(f"[DEVICE {index}] Opened: {path}")

        while True:
            report = device.read(64)

            if not report:
                continue

            print(
                f"[DEVICE {index}] {report}"
            )

    except Exception as error:
        print(
            f"[DEVICE {index}] ERROR: {error}"
        )

    finally:
        try:
            device.close()
        except Exception:
            pass

        print(
            f"[DEVICE {index}] Closed."
        )


threads = []

for index, path in enumerate(PATHS):
    thread = Thread(
        target=listen,
        args=(path, index),
        daemon=True,
    )

    threads.append(thread)
    thread.start()


print()
print("Both Logitech interfaces are listening.")
print("Press G1-G9.")
print("Press Ctrl+C to stop.")
print()

try:
    while True:
        pass

except KeyboardInterrupt:
    print("\nStopping...")
