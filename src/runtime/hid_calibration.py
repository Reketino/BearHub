import json
from pathlib import Path

import hid

class HIDCalibrator:
    def __init__(self, device_path: bytes):
        self.device_path = device_path
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
        
    def calibrate(self):
        self.device.open_path(self.device_path)
        
        try:
            for key_name in self.keys:
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
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                self.mapping,
                f,
                indent=4,
            )