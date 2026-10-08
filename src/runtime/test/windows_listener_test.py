from runtime.windows_macro_listener import WindowsMacroListener

def callback(key):
    print(f"CALLBACK: {key}")

listener = WindowsMacroListener()
listener.set_callback(callback)

listener.start()

try:
    input("Press Enter to stop...\n")
finally:
    listener.stop()