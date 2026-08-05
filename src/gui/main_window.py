from pathlib import Path

from PySide6.QtGui import QPixmap
from PySide6.QtCore import QThread, QTimer, Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QFileDialog,
    QDialog,
    QComboBox,
    QMessageBox,
    QGroupBox
)

from importers.ghub_importer import import_macros
from storage.profile_storage import ( 
    add_macro,
    save_profile,
    load_profiles,
    update_macro,
    delete_macro,
    is_key_available,
    )
from constants.g_keys import G_KEY_MAP
from constants.macro_types import TEXT
from models.macro import Macro
from runtime.macro_engine import MacroEngine
from runtime.calibration_worker import CalibrationWorker
from gui.macro_dialog import MacroDialog
from gui.controllers.macro_controller import MacroController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
                
        self.setup_window()
        self.create_widgets()
        self.create_layout()
       
        self.macro_controller = MacroController(self)
        
        self.connect_signals()
        
        
        self.macros = []
        self.profiles = []
        self.current_profile_id = None
        
        self.engine = MacroEngine()
        
        self.calibration_thread = None
        self.calibration_worker = None
     
        self.load_saved_profiles()
        
    
    def setup_window(self):
        self.setWindowTitle("Bearhub")
        self.resize(700, 500)
                
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.main_layout = QVBoxLayout(central_widget)
            
    def create_widgets(self):
            self.profile_selector = QComboBox()
        
            self.import_button = QPushButton("Import from Ghub")
           
            self.new_macro_button = QPushButton("New Macro")
            
            self.edit_macro_button = QPushButton("Edit Macro")
            self.edit_macro_button.setEnabled(False)
            
            self.delete_macro_button = QPushButton("Delete Macro")
            self.delete_macro_button.setEnabled(False)
            
            self.calibrate_button = QPushButton("Calibrate G-keys")
            
            self.start_button = QPushButton("Start Runtime")
            
            self.stop_button = QPushButton("Stop Runtime")
            self.stop_button.setEnabled(False)
           
            self.macro_list = QListWidget()
             
            self.details = QLabel("Select a macro")
            
            self.execute_button = QPushButton("Execute")
            
            self.status = QLabel("Ready")
            
            
    def create_layout(self):
        header_layout = QHBoxLayout()

        logo = QLabel()
        pixmap = QPixmap(
            str(self.get_assets_path("bearhub-logo.png"))
        )
        logo.setPixmap(
            pixmap.scaledToHeight(
                64,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

        title_layout = QVBoxLayout()

        title = QLabel("BearHub")
        title.setObjectName("title")

        subtitle = QLabel("Open Source Macro Manager")
        subtitle.setObjectName("subtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addWidget(logo)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        self.main_layout.addLayout(header_layout)
        self.main_layout.addSpacing(12)

        content_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 2)

        self.main_layout.addLayout(content_layout)

        profile_group = QGroupBox("Profile")
        actions_group = QGroupBox("Actions")
        runtime_group = QGroupBox("Runtime")

        left_layout.addWidget(profile_group)
        left_layout.addWidget(actions_group)
        left_layout.addWidget(runtime_group)
        left_layout.addStretch()

        profile_layout = QVBoxLayout(profile_group)

        profile_layout.addWidget(self.profile_selector)
        profile_layout.addWidget(self.import_button)

        actions_layout = QVBoxLayout(actions_group)

        actions_layout.addWidget(self.new_macro_button)
        actions_layout.addWidget(self.edit_macro_button)
        actions_layout.addWidget(self.delete_macro_button)
        actions_layout.addWidget(self.execute_button)

        runtime_layout = QVBoxLayout(runtime_group)

        runtime_layout.addWidget(self.calibrate_button)
        runtime_layout.addWidget(self.start_button)
        runtime_layout.addWidget(self.stop_button)

        right_layout.addWidget(self.macro_list)
        right_layout.addWidget(self.details)
        right_layout.addWidget(self.status)
        
    def connect_signals(self):
        self.profile_selector.currentIndexChanged.connect(
            self.change_profile
        )
        
        self.macro_list.currentRowChanged.connect(
            self.macro_controller.show_macro
        )
        self.import_button.clicked.connect(
            self.import_ghub
        )
        self.new_macro_button.clicked.connect(
            self.macro_controller.open_macro_dialog
        )
        self.edit_macro_button.clicked.connect(
            self.macro_controller.edit_selected_macro
        )
        self.delete_macro_button.clicked.connect(self.delete_selected_macro)
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
            self.macro_controller.execute_selected_macro
        )
        
            
    def get_assets_path(self, filename: str) -> Path:
        project_root = Path(__file__).resolve().parent.parent.parent
        return project_root / "assets" / filename
        
    #-------- IMPORT GHUB --------#
    
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
        
        
    #-------- DELETE SELECTED MACRO --------#
    
    def delete_selected_macro(self):
        row = self.macro_list.currentRow()
        
        if row < 0 or row >= len(self.macros):
            return
        
        if self.current_profile_id is None:
            self.status.setText(
                "No profile selected."
            )
            return
        
        macro = self.macros[row]
        
        answer = QMessageBox.question(
            self,
            "Delete Macro",
            f"Delete '{macro.name}'?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        
        if answer != QMessageBox.StandardButton.Yes:
            return
        
        success = delete_macro(
            self.current_profile_id,
            row,
            "src/storage/profile.json"
        )
        
        if not success:
            self.status.setText(
                "Could not delete macro."
            )
            return
        
        self.reload_current_profile()
        
        if self.macro_list.count() > 0:
            new_row = min(
                row,
                self.macro_list.count() - 1,
            )
            
            self.macro_list.setCurrentRow(
                new_row
            )
        
        self.status.setText(
            f"Deleted {macro.name}."
        )
                
    #-------- LOAD PROFILE --------#
        
    def load_profile(self, profile):
        self.current_profile_id = profile["id"]
        
        self.setWindowTitle(
            f"{profile['name']} - {profile['macro_count']} macros"
        )
        macros = []
        
        for macro_data in profile["macros"]:
            macros.append(
                Macro(
                    id="",
                    name=macro_data["name"],
                    value=macro_data.get(
                        "value",
                        macro_data.get("text", "")
                    ),
                    macro_type=macro_data.get(
                        "macro_type",
                        TEXT,
                        ),
                    profile_name=macro_data["preset"],
                    device_signature=macro_data["device"],
                    input_id=macro_data["input_id"],
                )
            )
            
        self.macro_controller.display_macros(macros)
        
    #-------- RELOAD CURRENT PROFILE --------#
        
    def reload_current_profile(self):
        profiles = load_profiles(
            "src/storage/profile.json"
        )
        
        profile = next(
            (
                profile
                for profile in profiles
                if profile.get("id")
                == self.current_profile_id
            ),
            None,
        )
        
        if profile is None:
            return
        
        self.load_profile(profile)
    
        
    
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
    
    #-------- CHANGE PROFILE --------#    
        
    def change_profile(self, index):
        if index < 0:
            return
        
        if index >= len(self.profiles):
            return
        
        profile = self.profiles[index]
        
        self.load_profile(profile)
        
    #-------- START RUNTIME --------#
        
    def start_runtime(self):
        self.engine.start()
        
        self.start_button.setEnabled(False)
        self.calibrate_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        self.status.setText(
            "Runtime started."
        )
    
    #-------- STOP RUNTIME --------#
        
    def stop_runtime(self):
        self.engine.stop()
        
        self.start_button.setEnabled(True)
        self.calibrate_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.status.setText(
            "Runtime stopped."
        )
    
    #-------- CALIBRATE G KEYS --------#
        
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
        
    #-------- CALIBRATION PROGRESS --------#
    
    def calibration_progress(self, key_name):
        self.status.setText(
            f"Press {key_name}..."
        )
        
    #-------- CALIBRATION FINISHED --------#
            
    def calibration_finished(self):
        self.status.setText(
            "Calibration completed."
        )
        
        self.calibrate_button.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
    #-------- CALIBRATION FAILED--------#
        
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
            

        
       