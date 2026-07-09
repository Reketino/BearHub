import hid
from threading import Thread

from runtime.hid_parser import parse_report


PATH = (
    b"\\\\?\\HID#VID_046D&PID_C547&MI_02&Col02"
    b"#8&324fa3f5&0&0001"
    b"#{4d1e55b2-f16f-11cf-88cb-001111000030}"
)

class MacroListener:
    def __init__(self):
        self.running = False
        self.callback = None
        self.thread = None
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
        try:
            self.device.open_path(PATH)
        
            while self.running:
                report = self.device.read(64)
                
                if not report:
                    continue
                key = parse_report(report)
            
                if not key:
                    continue
                print (key)
            
                if self.callback:
                    self.callback(key)
        except Exception as e:
            print(f"HID Error: {e}")
        
        finally:
            self.device.close()
        
    def stop(self):
        if not self.running:
            return
        self.running = False
        print("Stopped listening😶‍🌫️")