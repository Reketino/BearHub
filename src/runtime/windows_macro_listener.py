import time
from threading import Thread

import hid

from runtime.hid_device import find_device
from runtime.logitech.hidpp import HidppDevice
from runtime.logitech.g_keys import LogitechGKeys

class WindowsMacroListener:

    def __init__(self):
        self.callback = None
        self.running = False
        self.hook = None

    def set_callback(self, callback):
        self.callback = callback

    def start(self):
        if self.running:
            return

        self.running = True
        
        self.thread = Thread(
            target=self.listen,
            daemon=True,
        )
        
        self.thread.start()

        print("Windows G-key listener started.")
        print("Listening for G1-G9.")
        
    def listen(self):
        try:
            path = find_device()
            
            if path is None:
                print(
                    "No Logitech G-key HID device found."
                )
                
                self.running = False
                return
            

    def stop(self):
        if not self.running:
            return

        self.running = False
        
        self._close_device()
        
        print(
            "Windows G-key listener stopped."
        )
        
    def _close_device(self):
        if self.device is None:
            return
        
        try:
            self.device.close()
            
        except Exception:
            pass
        
        self.device = None