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
        self.device = hid.device()
        
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
        print("Listening for ya keys👂🏻")
        
    def listen(self):
        print("Listener thread started")
        try:
            path = find_device()
            self.device.open_path(path)
            print("HID device opened")
        
            while self.running:
                report = self.device.read(64)
                
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
            print(f"HID Error: {e}")
        
        finally:
            self.device.close()
            print("HID device closed")
        
    def stop(self):
        if not self.running:
            return
        self.running = False
        print("Stopped listening😶‍🌫️")