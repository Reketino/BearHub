from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
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

        self.macro_list = QListWidget()
        layout.addWidget(self.macro_list)

        db_path = "/home/bear/Nedlastinger/settings.db"
        data = import_macros(db_path)

        profiles = data["profiles"]["profiles"]
        my_profile = next(
            (
                p
                for p in profiles
                if p.get("name") in ("Ny profil", "New Profile")
            ),
            None,
        )

        if my_profile is None:
            self.macro_list.addItem("Fant ingen brukerprofil.")
            return

        self.macro_list.addItem(
            f"Profil: {my_profile.get('name')}"
        )

        print(f"\nFant profil: {my_profile.get('name')}\n")

        print("=== Slot IDs ===")
        for assignment in my_profile.get("assignments", []):
            slot = assignment.get("slotId", "")
            print(slot)
            self.macro_list.addItem(slot)

        print("\n=== Søker etter tekstmakroer ===")

        search_for_text(data, "{}")
        search_for_text(data, "()")
        search_for_text(data, "[]")
        search_for_text(data, "=>")
  