import json
from pathlib import Path

import hid

from runtime.hid_device import find_device

class HIDCalibrator:
    def __init__(self):
        self.device = hid.device()
        
        self.keys = [
            "G1",
            "G2",
            "G3",
            "G4",
            "G5",
            "G6",
            "G7",
            "G8",
            "G9",
        ]
        
        self.mapping = {}
        
    def calibrate(self, progress_callback=None):
        path = find_device()
        
        if path is None:
            raise RuntimeError("No compatible Logitech HID device found.")
        self.device.open_path(path)
        
        try:
            for key_name in self.keys:
                if progress_callback:
                    progress_callback(key_name)
                    
                print(f"\nPress {key_name}...")
                
                while True:
                    report = self.device.read(64)
                    if not report:
                        continue
                    code = report[4]
                    if code == 0:
                        continue
                    print(f"{key_name} -> {code}")
                    self.mapping[str(code)] = key_name
                    break
        
        finally:
            self.device.close()
            
    def save(self, output_file):
        Path(output_file).parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        with open(
            output_file, 
            "w", 
            encoding="utf-8",
            ) as f:
            json.dump(
                self.mapping,
                f,
                indent=4,
            )