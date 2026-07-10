from constants.hid_keys import HID_G_KEY_MAP

def parse_report(report):
    if len(report) < 5:
        return None
    
    code = report[4]
    
    if code == 0:
        return None
    
    return HID_G_KEY_MAP.get(code)