from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)
from constants.g_keys import G_KEY_MAP

class MacroDialog(QDialog):
    def __init__(self, parent=None, macro=None):
        super().__init__(parent)
        
        self.macro = macro
        self.setWindowTitle("New Macro")
        self.resize(400, 250)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        form_layout.addRow(
            "Name:",
            self.name_input,
        )
        
        self.key_input = QComboBox()
        self.key_input.addItems(
            [
                "G1",
                "G2",
                "G3",
                "G4",
                "G5",
                "G6",
                "G7",
                "G8",
                "G9",
            ]
        )
        
        form_layout.addRow(
            "G-key:",
            self.key_input,
        )
        
        self.text_input = QLineEdit()
        form_layout.addRow(
            "Text:",
            self.text_input,
        )
        
        layout.addLayout(form_layout)
        
        self.save_button = QPushButton(
            "Save Macro"
        )
        layout.addWidget(self.save_button)
        
        self.save_button.clicked.connect(
            self.accept
        )
        
        if self.macro is not None:
            self.setWindowTitle("Edit Macro")
            
            self.name_input.setText(
                self.macro.name
            )
            
            self.text_input.setText(
                self.macro.text
            )
            
            key_name = G_KEY_MAP.get(
                self.macro.input_id,
                "G1"
            )
            
            self.key_input.setCurrentText(
                key_name
            )
        
    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "key": self.key_input.currentText(),
            "text": self.text_input.text(),
        }
        