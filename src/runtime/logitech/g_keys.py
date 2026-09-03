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
        self.feature_index = feature_index
        
    def read_diversion(self) -> bool:
        report = self.hidpp.get_feature(
            self.feature_index
        )
        
        if len(report) < 5:
            raise RuntimeError(
                "Invalid GKEY HID++ response."
            )
            
        return report[4] != 0
    
    def enable_diversion(self) -> None:
        self.hidpp.set_feature(
            self.feature_index,
            GKEY_DIVERT_ENABLED,
        )