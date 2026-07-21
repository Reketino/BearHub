import hid
from threading import Thread

from runtime.hid_parser import parse_report
from runtime.hid_device import find_device


class MacroListener:
    def __init__(self):
        self.running = False
        self.callback = None
        self.thread = None
        self.last_key = None
        self.device = None
        
    def set_callback(self, callback):
        self.callback = callback
        
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.last_key = None
        
        self.thread = Thread(
            target=self.listen,
            daemon=True,
        )
        
        self.thread.start()
        print("Listening for ya keys👂🏻")
        
    def listen(self):
        print("Listener thread started")
        try:
            path = find_device()
            
            if path is None:
                raise RuntimeError(
                    "No compatible Logitech HID device found"
                )
                
            self.device = hid.device()
            self.device.open_path(path)
            
            print("HID device opened")
        
            while self.running:
                report = self.device.read(64)
                
                if not self.running:
                    break
                
                if not report:
                    continue
                print(f"Report: {report}")
                
                key = parse_report(report)
            
                if not key:
                    self.last_key = None
                    continue
                
                if key == self.last_key:
                    continue
                
                self.last_key = key
                
                print (key)
            
                if self.callback:
                    self.callback(key)
                    
        except Exception as e:
            if self.running:
                print(f"HID Error: {e}")
        
        finally: 
            if self.device is not None:
                try:
                    self.device.close()
                except Exception:
                    pass
                
                self.device = None
            self.running = False
            
            print("HID device closed")
        
    def stop(self):
        if not self.running:
            return
        
        self.running = False
        
        if (
            self.thread is not None
            and self.thread.is_alive()
        ):
            self.thread.join(timeout=1)
            
        self.thread = None
        print("Stopped listening😶‍🌫️")