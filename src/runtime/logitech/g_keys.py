from runtime.logitech.hidpp import (
    GKEY_FEATURE_ID,
    HidppDevice,
)

GKEY_FEATURE_INDEX = 0x10

GKEY_DIVERT_ENABLED = b"\x01"
GKEY_DIVERT_DISABLED = b"\x00"

class LogitechGKeys:
    
    def __init__(
        self,
        hidpp: HidppDevice,
        feature_index: int = GKEY_FEATURE_INDEX
    ):
        self.hidpp = hidpp
        