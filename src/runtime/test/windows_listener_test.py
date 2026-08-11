from runtime.windows_macro_listener import WindowsMacroListener

def on_key_pressed(key):
    print(f"CALLBACK: {key}")
    
listener = WindowsMacroListener()

listener.set_callback(
    on_key_pressed
)

listener.start()

print()
print("Press G1-G9.")
print("Press Ctrl + C to stop.")
print()