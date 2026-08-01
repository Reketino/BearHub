BEARHUB_STYLE = """
QMainWindow {
    background-color: #151719;
}

QWidget {
    color: #f2f4f5;
    font-family: "Segoe UI";
    font-size: 14px;
}

QLabel {
    background-color: transparent;
}

QComboBox {
    background-color: #202428;
    border: 1px solid #343a40;
    border-radius: 7px;
    padding: 8px 10px;
    min-height: 22px;
}

QComboBox:hover {
    border: 1px solid #00b7f0;
}

QComboBox:focus {
    border: 1px solid #00b7f0;
}

QComboBox QAbstractItemView {
    background-color: #202428;
    color: #f2f4f5;
    border: 1px solid #343a40;
    selection-background-color: #00aee8;
    selection-color: #ffffff;
}

QPushButton {
    background-color: #24282c;
    border: 1px solid #363c42;
    border-radius: 7px;
    padding: 8px 14px;
    min-height: 22px; 
}

QPushButton:hover {
    background-color: #2b3035;
    border: 1px solid #00b7f0;
}

QPushButton:pressed {
    background-color: #1d2125;
}

QPushButton:disabled {
    background-color: #1c1f22;
    color: #62686d;
    border: 1px solid #292d31; 
}

QPushButton#primaryButton {
    background-color: #00aee8;
    color: #071015;
    border: 1px solid #00bfff;
    font-weight: 600; 
}

QPushButton#primaryButton:hover {
    background-color: #18c2f5;
}

QPushButton#dangerButton:hover {
    border: 1px solid #d85c5c;
    color: #ff8080;
}

QListWidget {
    background-color: #1d2023;
    border: 1px solid #30353a;
    border-radius: 8px;
    padding: 6px;
    outline: none;
}

QListWidget::item {
    border-radius: 6px;
    padding: 10px;
    margin: 2px;
}

QListWidget::item:hover {
    background-color: #272c30;
}

QListWidget::item:selected {
    background-color: #123b49;
    color: #ffffff;
    border-left: 3px solid #00b7f0;
}
"""