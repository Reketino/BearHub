import sys
from pathlib import Path

from PySide6 import QIcon
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

from gui.main_window import MainWindow

app = QApplication([])

window = MainWindow()
window.show()

app.exec()