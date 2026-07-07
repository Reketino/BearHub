import keyboard

class MacroListener:
    def __init__(self):
        self.running = False
        self.callback = None
    def set_callback(self, callback):
        self.callback = callback
        
    def start(self):
        if self.running:
            return
        self.running = True
        keyboard.on_press(self.on_press)
        print("Listening for ya keys👂🏻")
        
    def stop(self):
        if not self.running:
            return
        self.running = False
        keyboard.unhook_all()
        
        print("Stopped listening😶‍🌫️")
        
    def on_press(self, event):
        if not self.running:
            return
        print(event.name)
        if self.callback:
            self.callback(event.name)