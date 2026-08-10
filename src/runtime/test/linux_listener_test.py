from select import select

from evdev import InputDevice


PATHS = [
    "/dev/input/event3",
    "/dev/input/event5",
]


devices = []

for path in PATHS:
    try:
        device = InputDevice(path)
        devices.append(device)

        print(
            f"Opened {path}: "
            f"{device.name}"
        )

    except Exception as error:
        print(
            f"Could not open {path}: "
            f"{error}"
        )


print()
print("Listening for ALL events.")
print("Press G1-G9.")
print("Press Ctrl+C to stop.")
print()


try:
    while True:
        readable, _, _ = select(
            devices,
            [],
            [],
            1.0,
        )

        for device in readable:
            for event in device.read():
                print(
                    f"[{device.path}] "
                    f"type={event.type} "
                    f"code={event.code} "
                    f"value={event.value}"
                )

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    for device in devices:
        device.close()

    print("Closed.")