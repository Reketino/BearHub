import time

import hid

HIDPP_SHORT_REPORT_ID = 0x10
HIDPP_LONG_REPORT_ID = 0x11

GKEY_FEATURE_ID = 0x8010

HIDPP_DEVICE_ID = 0x01

HIDPP_READ_FUNCTION = 0x00
HIDPP_WRITE_FUNCTION = 0x10

class HidppError(Exception):
    """ Base exception for Logitech HID++ communication"""
    
class HIDppDevice:
    def __init__(
        self,
        device: hid.device,
        device_id: int = HIDPP_DEVICE_ID,
        ):
        self.device = device
        self.device_id = device_id