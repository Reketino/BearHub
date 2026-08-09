import hid


LOGITECH_VENDOR_ID = 0x046D
LIGHTSPEED_RECEIVER_PID = 0xC547

G_KEY_USAGE_PAGE = 0xFF00
G_KEY_USAGE = 0x02


def main():
    devices = hid.enumerate()

    print("=" * 70)
    print("LOGITECH LIGHTSPEED HID DEVICES")
    print("=" * 70)

    found = 0

    for device in devices:
        if (
            device["vendor_id"] != LOGITECH_VENDOR_ID
            or device["product_id"] != LIGHTSPEED_RECEIVER_PID
        ):
            continue

        found += 1

    print()
    print(f"DEVICE {found}")
    print("-" * 70)
    print(f"Path        : {device['path']}")
    print(f"Interface   : {device.get('interface_number')}")
    print(f"Usage Page  : {device.get('usage_page')}")
    print(f"Usage       : {device.get('usage')}")
    print(f"Product     : {device.get('product_string')}")

    is_g_key = (
        device.get("usage_page") == G_KEY_USAGE_PAGE
        and device.get("usage") == G_KEY_USAGE
    )

    print(f"G-key       : {is_g_key}")

    print()
    print("=" * 70)
    print(f"Found {found} Logitech receiver HID interfaces.")
    print("=" * 70)


if __name__ == "__main__":
    main()