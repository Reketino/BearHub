import keyboard

class MacroListener:
    def __init__(self):
        self.running = False
        
    def start(self):
        self.running = True
        
        print("Listening for ya keys👂🏻")
        
    def stop(self):
        self.running = False
        
        print("Stopped listening😶‍🌫️")