import hid

from src.runtime.hid_parser import parse_report

PATH = (
    b"\\\\?\\HID#VID_046D&PID_C547&MI_02&Col02"
    b"#8&324fa3f5&0&0001"
    b"#{4d1e55b2-f16f-11cf-88cb-001111000030}"
)

device = hid.device()
device.open_path(PATH)
print("Connected")
print("Press G-keys...\n")

# Run script w: python -m src.runtime.hid_reader

while True:
    report = device.read(64)
    
    if report:
        key = parse_report(report)
        if key:
            print(key)