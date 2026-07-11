import json

HID_G_KEY_MAP = {}

try:
    with open(
        "src/storage/hid_mapping.json",
        encoding="utf-8",
    ) as f:
        HID_G_KEY_MAP = json.load(f)
except FileNotFoundError:
    print("No HID mapping found.")
    
def parse_report(report):
    if len(report) < 5:
        return None
    
    code = report[4]
    
    if code == 0:
        return None
    
    return HID_G_KEY_MAP.get(str(code))