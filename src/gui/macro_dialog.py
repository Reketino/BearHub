from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

class MacroDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
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
        
    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "key": self.key_input.currentText(),
            "text": self.text_input.text(),
        }