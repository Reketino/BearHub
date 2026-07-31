import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

from gui.main_window import MainWindow

def get_assets_path(filename: str) -> Path:
    project_root = Path(__file__).resolve().parent.parent
    return project_root / "assets" / filename

def main():    
    app = QApplication(sys.argv)
    
    app.setApplicationName("BearHub")
    app.setApplicationDisplayName("Bearhub")
    app.setWindowIcon(
        QIcon(str(get_assets_path("bearhub-icon.png")))
    )

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()
