
import sys

from PySide6.QtCore import QObject, Signal

from runtime.hid_calibration import HIDCalibrator
from runtime.hid_parser import load_mapping


class CalibrationWorker(QObject):
    finished = Signal()
    error = Signal(str)
    progress = Signal(str)

    def run(self) -> None:
        try:
            if sys.platform.startswith("linux"):
                from runtime.linux.g915_calibrator import (
                    G915XCalibrator,
                )

                calibrator = G915XCalibrator()

                calibrator.calibrate(
                    self.progress.emit,
                )

            elif sys.platform == "win32":
                calibrator = HIDCalibrator()

                calibrator.calibrate(
                    self.progress.emit,
                )

                calibrator.save(
                    "src/storage/hid_mapping.json"
                )

                load_mapping()

            else:
                raise RuntimeError(
                    f"Unsupported platform: {sys.platform}"
                )

            self.finished.emit()

        except Exception as error:
            self.error.emit(str(error))
