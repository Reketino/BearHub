import hid

LOGITECH_VENDOR_ID = 0x046D
LIGHTSPEED_RECEIVER_PID = 0xC547
G_KEY_USAGE_PAGE = 65280
G_KEY_USAGE = 2

def find_device():
    
    for device in hid.enumerate():
        if ( 
            device["vendor_id"] == LOGITECH_VENDOR_ID
            and device["product_id"] == LIGHTSPEED_RECEIVER_PID
            and device["usage_page"] == G_KEY_USAGE_PAGE
            and device["usage"] == G_KEY_USAGE
        ):
                print(
                    f"Found Logitech receiver"
                    f"(interface {device['interface_number']})"
                )
                
                return device["path"]
            
    return None