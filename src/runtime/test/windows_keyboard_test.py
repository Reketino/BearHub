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

def on_key_pressed(event):
    key = event.name.lower()
    
    if key in KEYS:
        print(
            f"Keyboard event: {key.upper()} -> {KEYS[key]}"
        )
        
print("Windows keyboard listener started.")
print()
print("Listening for F13-F21.")
print()
print("G1 -> F13")
print("G2 -> F14")
print("G3 -> F15")
print("G4 -> F16")
print("G5 -> F17")
print("G6 -> F18")
print("G7 -> F19")
print("G8 -> F20")
print("G9 -> F21")
print()
print("Press CTRL+C to stop")
print()

keyboard.hook(on_key_pressed)

try:
    keyboard.wait()
    
except KeyboardInterrupt:
    print()
    print("Stopping...")
    