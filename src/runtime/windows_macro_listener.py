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
        self.thread = None
        
        self.device = None
        self.hidpp = None
        self.gkeys = None

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
            
            print(
                f"Opening Logitech HID device: {path}"
            )
            
            self.device = hid.device()
            self.device.set_nonblocking(True)
            
            print("HID device opened.")
            
            self.hidpp = HidppDevice(
                self.device
            )
            
            self.gkeys = LogitechGKeys(
                self.hidpp
            )
            
            print("Enabling G-key diversion...")
            
            self.gkeys.enable_diversion()
            
            print("G-key diversion enabled.")
            
            while self.running:
                
                report = self.device.read(64)
                
                if not report:
                    time.sleep(0.005)
                    continue
                
                print(f"Report: {report}")
                
                key_code = self.gkeys.handle_notification(
                    report
                )
            
            
            

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