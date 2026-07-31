import sys
from pathlib import Path

from PySide6 import QIcon
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

from gui.main_window import MainWindow

def get_assets(filename: str) -> Path:
    project_root = Path(__file__).resolve().parent.parent
    return project_root / "assets" / filename

app = QApplication([])

window = MainWindow()
window.show()

app.exec()