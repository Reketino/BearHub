from PySide6.QtCore import QThread, QTimer

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QFileDialog,
    QDialog,
    QComboBox,
)

from importers.ghub_importer import import_macros
from storage.profile_storage import ( 
    add_macro,
    save_profile,
    load_profiles,
    )
from constants.g_keys import G_KEY_MAP
from models.macro import Macro
from runtime.macro_engine import MacroEngine
from runtime.calibration_worker import CalibrationWorker
from gui.macro_dialog import MacroDialog

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
        
        self.profile_selector = QComboBox()
        layout.addWidget(self.profile_selector)

        self.import_button = QPushButton("Import from Ghub")
        layout.addWidget(self.import_button)
        
        self.new_macro_button = QPushButton("New Macro")
        layout.addWidget(self.new_macro_button)
        
        self.calibrate_button = QPushButton("Calibrate G-keys")
        layout.addWidget(self.calibrate_button)
        
        self.start_button = QPushButton("Start Runtime")
        layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Runtime")
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        self.macro_list = QListWidget()
        layout.addWidget(self.macro_list)
        
        self.details = QLabel("Select a macro")
        layout.addWidget(self.details)
        
        self.execute_button = QPushButton("Execute")
        layout.addWidget(self.execute_button)
        
        self.status = QLabel("Ready")
        layout.addWidget(self.status)
        
        self.macros = []
        self.profiles = []
        
        self.engine = MacroEngine()
        
        self.calibration_thread = None
        self.calibration_worker = None
        
        self.profile_selector.currentIndexChanged.connect(
            self.change_profile
        )
        
        self.macro_list.currentRowChanged.connect(
            self.show_macro
        )
        self.import_button.clicked.connect(
            self.import_ghub
        )
        self.new_macro_button.clicked.connect(
            self.open_macro_dialog
        )
        self.calibrate_button.clicked.connect(
            self.calibrate_g_keys
        )
        self.start_button.clicked.connect(
            self.start_runtime
        )
        self.stop_button.clicked.connect(
            self.stop_runtime
        )
        self.execute_button.clicked.connect(
            self.execute_selected_macro
        )
        
        self.load_saved_profiles()
    
    def import_ghub(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose settings.db",
            "",
            "Database (*.db)"
        )
        
        if not file_path:
            return
       
        macros = import_macros(file_path)
        
        save_profile(
            macros,
            "src/storage/profile.json"
        )
        
        self.load_saved_profiles()
        self.status.setText(
            f"Imported {len(macros)} macros."
        )
 
    #-------- DISPLAY MACROS --------#
  
    def display_macros(self, macros):
        self.macros = macros
        self.engine.load_profile(macros)
        self.macro_list.clear()
        
        for macro in macros:
            key_name = G_KEY_MAP.get(
                macro.input_id,
                "Unbound"
            )
            
            self.macro_list.addItem(
                f"{macro.name} [{key_name}]"
            )
    
    #-------- SHOW MACRO --------#
            
    def show_macro(self, row):
        if row < 0 or row >= len(self.macros):
            self.details.setText(
                "Select a macro"
            )
            return
        
        macro = self.macros[row]
        
        key_name = G_KEY_MAP.get(
            macro.input_id,
            "Unbound"
        )
        
        self.details.setText(
            f"Name: {macro.name}\n\n"
            f"Text:\n{macro.text}\n\n"
            f"Key: {key_name}\n"
            f"Preset: {macro.profile_name}\n"
            f"Device: {macro.device_signature}"
        )
        
        self.status.setText(
            f"Selected {macro.name}"
        )
        
    #-------- OPEN MACRO DIALOG --------#
        
    def open_macro_dialog(self):
        dialog = MacroDialog(self)
        
        result = dialog.exec()
        
        if result != QDialog.DialogCode.Accepted:
            return
        
        data = dialog.get_data()
        
        input_id = next(
            (
                input_id
                for input_id, key_name in G_KEY_MAP.items()
                if key_name == data["key"]
            ),
            None,
        )
        
        if input_id is None:
            self.status.setText(
                f"Could not find input ID for {data['key']}."
            )
            return
        
        macro = Macro(
            id="",
            name=data["name"],
            text=data["text"],
            macro_type="TEXT",
            profile_name="BearHub",
            device_signature="",
            input_id=input_id,
        )
        
        add_macro(
            macro,
            "src/storage/profile.json",
        )
        
        self.load_saved_profiles()
        
        bearhub_index = next(
            (
                index
                for index, profile in enumerate(self.profiles)
                if profile.get("id") == "bearhub"
            ),
            -1
        )
        
        if bearhub_index >= 0:
            self.profile_selector.setCurrentIndex(
                bearhub_index
            )
            self.change_profile(
                bearhub_index
            )
        
        self.status.setText(
            f"Saved {macro.name}."
        )
        
    #-------- LOAD PROFILE --------#
        
    def load_profile(self, profile):
        self.setWindowTitle(
            f"{profile['name']} - {profile['macro_count']} macros"
        )
        macros = []
        
        for macro_data in profile["macros"]:
            macros.append(
                Macro(
                    id="",
                    name=macro_data["name"],
                    text=macro_data["text"],
                    macro_type="TEXT",
                    profile_name=macro_data["preset"],
                    device_signature=macro_data["device"],
                    input_id=macro_data["input_id"],
                )
            )
            
        self.display_macros(macros)
    
    #-------- LOAD SAVED PROFILES --------#
     
    def load_saved_profiles(self):
        self.profiles = load_profiles(
            "src/storage/profile.json"
        )
        
        self.profile_selector.clear()
        
        if not self.profiles:
            return
        
        for profile in self.profiles:
            self.profile_selector.addItem(
                profile["name"]
            )
        
        self.profile_selector.setCurrentIndex(0)
        
        
    def change_profile(self, index):
        if index < 0:
            return
        
        if index >= len(self.profiles):
            return
        
        profile = self.profiles[index]
        
        self.load_profile(profile)
        
        
    def execute_selected_macro(self):
        row = self.macro_list.currentRow()
        
        if row < 0:
            return
        
        macro = self.macros[row]
        
        self.status.setText(
            f"Executing {macro.name} in 2 seconds..."
        )
        
        QTimer.singleShot(
            2000,
            lambda: self.execute_macro(macro)
        )
    
    def execute_macro(self, macro):
        self.engine.execute_macro(macro)
        self.status.setText(
            f"Executed {macro.name}"
        )
        
    def start_runtime(self):
        self.engine.start()
        
        self.start_button.setEnabled(False)
        self.calibrate_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        self.status.setText(
            "Runtime started."
        )
        
    def stop_runtime(self):
        self.engine.stop()
        
        self.start_button.setEnabled(True)
        self.calibrate_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.status.setText(
            "Runtime stopped."
        )
        
    def calibrate_g_keys(self):
        self.status.setText(
            "Starting calibration..."
        )
        
        self.calibrate_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        self.calibration_thread = QThread()
        self.calibration_worker = CalibrationWorker()
        
        self.calibration_worker.moveToThread(
            self.calibration_thread
        )
        
        self.calibration_thread.started.connect(
            self.calibration_worker.run
        )
        
        self.calibration_worker.finished.connect(
            self.calibration_finished
        )
        
        self.calibration_worker.progress.connect(
            self.calibration_progress
        )
        
        self.calibration_worker.error.connect(
            self.calibration_failed
        )
        
        self.calibration_worker.finished.connect(
            self.calibration_thread.quit
        )
        self.calibration_worker.error.connect(
            self.calibration_thread.quit
        )
        self.calibration_worker.finished.connect(
            self.calibration_worker.deleteLater
        )
        self.calibration_worker.error.connect(
            self.calibration_worker.deleteLater
        )
        self.calibration_thread.finished.connect(
            self.calibration_thread.deleteLater
        )
        self.calibration_thread.finished.connect(
            self.calibration_cleanup
        )
        
        self.calibration_thread.start()
        
    
    def calibration_progress(self, key_name):
        self.status.setText(
            f"Press {key_name}..."
        )
            
    def calibration_finished(self):
        self.status.setText(
            "Calibration completed."
        )
        
        self.calibrate_button.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
    def calibration_failed(self, message):
        self.status.setText(
            "Calibration failed."
        )
        
        self.calibrate_button.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
                
        print(
            f"Calibration error: {message}"
        )
            
    def calibration_cleanup(self):
        self.calibration_worker = None
        self.calibration_thread = None
            

        
       