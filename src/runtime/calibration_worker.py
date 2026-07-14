from PySide6.QtCore import QObject, Signal

from runtime.hid_calibration import HIDCalibrator
from runtime.hid_parser import load_mapping

class CalibrationWorker(QObject):
    finished = Signal()
    error = Signal(str)
    
    def run(self):
        try:
            calibrator = HIDCalibrator()
            
            calibrator.calibrate()
            
            calibrator.save(
                "src/storage/hid_maping.json"
            )
            
            load_mapping()
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))