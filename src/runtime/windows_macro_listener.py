import time
from threading import Thread

import hid

from runtime.hid_device import find_device
from runtime.hid_parser import parse_report

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
                print("No Logitech G-key HID device found.")
                self.running = False
                return
            
            print(
                f"Opening Logitech HID device: {path}"
            )
            
            self.device = hid.device()
            
            self.device.open_path(path)
            
            self.device.set_nonblocking(True)
            
            print("HID device opened.")
            
            while self.running:
                report = self.device.read(64)
                
                if not report:
                    time.sleep(0.005)
                    continue
                
                print(
                    f"Report: {report}"
                )
                
                g_key = parse_report(report)
                
                if g_key is None:
                    continue
                
                print(
                    f"Pressed {g_key}"
                )
                
                if self.callback is not None:
                    self.callback(g_key)
                    
        except Exception as error:
            if self.running:
                print(
                    f"Windows G-key listener error: {error}"
                )
        
        finally:
            self._close_device()
            

    def stop(self):
        if not self.running:
            return

        self.running = False
        print("Windows G-key listener stopped.")