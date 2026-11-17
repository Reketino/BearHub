
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from constants.g_keys import G_KEY_MAP


KEYBOARD_KEYS = [
    ("A", "a"),
    ("B", "b"),
    ("C", "c"),
    ("D", "d"),
    ("E", "e"),
    ("F", "f"),
    ("G", "g"),
    ("H", "h"),
    ("I", "i"),
    ("J", "j"),
    ("K", "k"),
    ("L", "l"),
    ("M", "m"),
    ("N", "n"),
    ("O", "o"),
    ("P", "p"),
    ("Q", "q"),
    ("R", "r"),
    ("S", "s"),
    ("T", "t"),
    ("U", "u"),
    ("V", "v"),
    ("W", "w"),
    ("X", "x"),
    ("Y", "y"),
    ("Z", "z"),
    *[(str(number), str(number)) for number in range(10)],
    ("Enter", "Return"),
    ("Space", "space"),
    ("Tab", "Tab"),
    ("Escape", "Escape"),
    ("Backspace", "BackSpace"),
    ("Delete", "Delete"),
    ("Insert", "Insert"),
    ("Home", "Home"),
    ("End", "End"),
    ("Page Up", "Page_Up"),
    ("Page Down", "Page_Down"),
    ("Arrow Up", "Up"),
    ("Arrow Down", "Down"),
    ("Arrow Left", "Left"),
    ("Arrow Right", "Right"),
    *[(f"F{number}", f"F{number}") for number in range(1, 13)],
    ("Minus", "minus"),
    ("Equal", "equal"),
    ("Left Bracket", "bracketleft"),
    ("Right Bracket", "bracketright"),
    ("Backslash", "backslash"),
    ("Semicolon", "semicolon"),
    ("Apostrophe", "apostrophe"),
    ("Comma", "comma"),
    ("Period", "period"),
    ("Slash", "slash"),
    ("Grave", "grave"),
]


class MacroDialog(QDialog):
    def __init__(self, parent=None, macro=None):
        super().__init__(parent)

        self.macro = macro

        self.setWindowTitle(
            "Edit Macro" if macro else "New Macro"
        )
        self.resize(420, 320)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)

        self.trigger_type_input = QComboBox()
        self.trigger_type_input.addItem("G-key", "g_key")
        self.trigger_type_input.addItem("Keyboard", "keyboard")

        form_layout.addRow(
            "Trigger type:",
            self.trigger_type_input,
        )

        self.trigger_key_input = QComboBox()

        form_layout.addRow(
            "Trigger key:",
            self.trigger_key_input,
        )

        self.behavior_label = QLabel("Key behavior:")

        self.suppress_trigger_input = QCheckBox(
            "Suppress original key press"
        )
        self.suppress_trigger_input.setChecked(True)

        form_layout.addRow(
            self.behavior_label,
            self.suppress_trigger_input,
        )

        self.text_input = QLineEdit()
        form_layout.addRow("Value:", self.text_input)

        layout.addLayout(form_layout)

        self.save_button = QPushButton("Save Macro")
        layout.addWidget(self.save_button)

        self.trigger_type_input.currentIndexChanged.connect(
            self.update_trigger_keys
        )

        self.save_button.clicked.connect(
            self.validate_and_accept
        )

        self.update_trigger_keys()

        if self.macro is not None:
            self.load_macro()

    def update_trigger_keys(self):
        trigger_type = self.trigger_type_input.currentData()

        self.trigger_key_input.clear()

        if trigger_type == "g_key":
            for key_name in G_KEY_MAP.values():
                self.trigger_key_input.addItem(
                    key_name,
                    key_name,
                )

        else:
            for label, key_value in KEYBOARD_KEYS:
                self.trigger_key_input.addItem(
                    label,
                    key_value,
                )

        is_keyboard = trigger_type == "keyboard"

        self.behavior_label.setVisible(is_keyboard)
        self.suppress_trigger_input.setVisible(is_keyboard)

    def load_macro(self):
        self.name_input.setText(self.macro.name)
        self.text_input.setText(self.macro.value)

        trigger_type = self.macro.trigger_type or "g_key"

        self.suppress_trigger_input.setChecked(
            self.macro.suppress_trigger
        )

        trigger_index = self.trigger_type_input.findData(
            trigger_type
        )

        if trigger_index >= 0:
            self.trigger_type_input.setCurrentIndex(
                trigger_index
            )

        self.update_trigger_keys()

        trigger_value = self.macro.trigger_value

        if not trigger_value and trigger_type == "g_key":
            trigger_value = G_KEY_MAP.get(
                self.macro.input_id,
                "",
            )

        key_index = self.trigger_key_input.findData(
            trigger_value
        )

        if key_index >= 0:
            self.trigger_key_input.setCurrentIndex(key_index)

    def validate_and_accept(self):
        name = self.name_input.text().strip()
        value = self.text_input.text().strip()

        if not name:
            QMessageBox.warning(
                self,
                "Missing name",
                "Macro name cannot be empty.",
            )
            self.name_input.setFocus()
            return

        if not value:
            QMessageBox.warning(
                self,
                "Missing value",
                "Macro value cannot be empty.",
            )
            self.text_input.setFocus()
            return

        if not self.trigger_key_input.currentData():
            QMessageBox.warning(
                self,
                "Missing trigger",
                "Select a trigger key.",
            )
            self.trigger_key_input.setFocus()
            return

        self.accept()

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "value": self.text_input.text().strip(),
            "trigger_type": self.trigger_type_input.currentData(),
            "trigger_value": self.trigger_key_input.currentData(),
            "suppress_trigger": (
                self.suppress_trigger_input.isChecked()
                if self.trigger_type_input.currentData() == "keyboard"
                else True
            ),
        }
