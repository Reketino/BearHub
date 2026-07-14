from PySide6.QtCore import QObject, Signal

from runtime.hid_calibration import HIDCalibrator
from runtime.hid_parser import load_mapping

class CalibrationWorker(QObject):