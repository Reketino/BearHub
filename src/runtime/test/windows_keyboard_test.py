import time

import keyboard


KEYS = {
    "f13": "G1",
    "f14": "G2",
    "f15": "G3",
    "f16": "G4",
    "f17": "G5",
    "f18": "G6",
    "f19": "G7",
    "f20": "G8",
    "f21": "G9",
}


last_event_time = None


def on_key_event(event):
    global last_event_time

    key = event.name.lower()

    if key not in KEYS:
        return

    now = time.perf_counter()

    if last_event_time is None:
        delta_ms = 0.0
    else:
        delta_ms = (now - last_event_time) * 1000

    last_event_time = now

    print(
        f"EVENT "
        f"type={event.event_type:<3} "
        f"key={key.upper():<3} "
        f"scan_code={event.scan_code:<3} "
        f"delta={delta_ms:>7.2f} ms"
    )


print("Windows keyboard diagnostic started.")
print()
print("Press G2 once.")
print("Then press Ctrl+C to stop.")
print()


keyboard.hook(on_key_event)


try:
    keyboard.wait()

except KeyboardInterrupt:
    print()
    print("Stopping...")

finally:
    keyboard.unhook_all()
    print("Windows keyboard diagnostic stopped.")