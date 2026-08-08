import hid

print("=" * 60)
print("Avaliable HID devices")
print("=" * 60)

devices = hid.enumerate()

for device in devices:
    print(f"Vendor ID : {hex(device['vendor_id'])}")
    print(f"Product ID : {hex(device['product_id'])}")
    print(f"Manufacturer : {device.get('manufacturer_string')}")
    print(f"Product : {device.get('product_string')}")
    print(f"Interface : {device.get('interface_number')}")
    print(f"Usage Page : {device.get('usage_page')}")
    print(f"Usage : {device.get('usage')}")
    print(f"Path: {device['path']}")
    print("=" * 60)