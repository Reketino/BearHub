
import unittest

from runtime.linux.g915_parser import G915XParser


REPORT_LENGTH = 17


def create_report(
    byte_14: int = 0,
    byte_15: int = 0,
) -> bytes:
    """Create a simulated G915 X HID report."""

    report = bytearray(REPORT_LENGTH)

    report[0] = 0x01
    report[14] = byte_14
    report[15] = byte_15

    return bytes(report)


class TestG915XParser(unittest.TestCase):

    def setUp(self):
        self.parser = G915XParser()

    def test_g1_press(self):
        report = create_report(byte_14=0x10)

        events = self.parser.parse_report(report)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].key, "G1")
        self.assertTrue(events[0].pressed)

    def test_g1_release(self):
        self.parser.parse_report(
            create_report(byte_14=0x10)
        )

        events = self.parser.parse_report(
            create_report()
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].key, "G1")
        self.assertFalse(events[0].pressed)

    def test_multiple_keys_pressed(self):
        report = create_report(
            byte_14=0x30,
        )

        events = self.parser.parse_report(report)

        self.assertEqual(
            [event.key for event in events],
            ["G1", "G2"],
        )

        self.assertTrue(
            all(event.pressed for event in events)
        )

    def test_holding_g1_and_pressing_g2(self):
        self.parser.parse_report(
            create_report(byte_14=0x10)
        )

        events = self.parser.parse_report(
            create_report(byte_14=0x30)
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].key, "G2")
        self.assertTrue(events[0].pressed)

    def test_release_g2_while_holding_g1(self):
        self.parser.parse_report(
            create_report(byte_14=0x30)
        )

        events = self.parser.parse_report(
            create_report(byte_14=0x10)
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].key, "G2")
        self.assertFalse(events[0].pressed)

    def test_g1_and_g5_simultaneously(self):
        report = create_report(
            byte_14=0x10,
            byte_15=0x01,
        )

        events = self.parser.parse_report(report)

        self.assertEqual(
            [event.key for event in events],
            ["G1", "G5"],
        )

    def test_invalid_report_length(self):
        events = self.parser.parse_report(b"\x01\x02")

        self.assertEqual(events, [])

    def test_invalid_report_id(self):
        report = bytearray(create_report())
        report[0] = 0x02

        events = self.parser.parse_report(bytes(report))

        self.assertEqual(events, [])

    def test_reset(self):
        self.parser.parse_report(
            create_report(byte_14=0x10)
        )

        self.parser.reset()

        events = self.parser.parse_report(
            create_report(byte_14=0x10)
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].key, "G1")
        self.assertTrue(events[0].pressed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
