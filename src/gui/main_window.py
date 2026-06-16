from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QFileDialog,
)

from importers.ghub_importer import import_macros
import pprint

def search_for_text(obj, needle, path="root"):
    if isinstance(obj, dict):
        for key, value in obj.items():
            search_for_text(value, needle, f"{path}/{key}")

    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            search_for_text(item, needle, f"{path}[{index}]")

    elif isinstance(obj, str):
        if needle in obj:
            print(f"\nFUNNET '{needle}'")
            print(path)
            print(obj)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bearhub")
        self.resize(700, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        title = QLabel("BearHub")
        layout.addWidget(title)

        self.import_button = QPushButton("Import from H hub")
        layout.addWidget(self.import_button)
        self.import_button.clicked.connect(self.import_ghub)

        self.macro_list = QListWidget()
        layout.addWidget(self.macro_list)

        db_path = "/home/bear/Nedlastinger/settings.db"
       
        macros = import_macros(db_path)
        
        print("We found your {len(macros)} macros\n")
       