from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox, QDialog

from gui.macro_dialog import MacroDialog
from constants.g_keys import G_KEY_MAP
from models.macro import Macro
from constants.macro_types import TEXT
from storage.profile_storage import (
    add_macro,
    is_key_available,
)

class MacroController:
    def __init__(self, window):
        self.view = window
        
     #-------- DISPLAY MACROS --------#
      
    def display_macros(self, macros):
        self.view.macros = macros
        self.view.engine.load_profile(macros)
        self.view.macro_list.clear()
            
        for macro in macros:
            key_name = G_KEY_MAP.get(
                macro.input_id,
                "Unbound"
            )
                
            self.view.macro_list.addItem(
                f"{macro.name} [{key_name}]"
            )
            
    
        #-------- SHOW MACRO --------#
            
    def show_macro(self, row):
        if row < 0 or row >= len(self.view.macros):
            self.view.edit_macro_button.setEnabled(False)
            self.view.delete_macro_button.setEnabled(False)
            return
        
        self.view.edit_macro_button.setEnabled(True)
        self.view.delete_macro_button.setEnabled(True)
        
        macro = self.view.macros[row]
        
        key_name = G_KEY_MAP.get(
            macro.input_id,
            "Unbound"
        )
        
        self.view.details.setText(
            f"Name: {macro.name}\n\n"
            f"Value:\n{macro.value}\n\n"
            f"Key: {key_name}\n"
            f"Preset: {macro.profile_name}\n"
            f"Device: {macro.device_signature}"
        )
        
        self.view.status.setText(
            f"Selected {macro.name}"
        )
        
    
    #-------- EXECUTE SELECTED MACROS --------#
            
    def execute_selected_macro(self):
        row = self.view.macro_list.currentRow()
            
        if row < 0:
                return
            
        macro = self.view.macros[row]
            
        self.view.status.setText(
            f"Executing {macro.name} in 2 seconds..."
        )
            
        QTimer.singleShot(
            2000,
            lambda: self.execute_macro(macro)
        )
        
    
    #-------- EXECUTE MACRO --------#
        
    def execute_macro(self, macro):
        self.view.engine.execute_macro(macro)
        self.view.status.setText(
            f"Executed {macro.name}"
        )
        
    
     #-------- OPEN MACRO DIALOG --------#
            
    def open_macro_dialog(self):
        dialog = MacroDialog(self.view)
            
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
            self.view.status.setText(
                f"Could not find input ID for {data['key']}."
            )
            return
            
        if not is_key_available(
            "bearhub",
            input_id,
            "src/storage/profile.json",
        ):
            QMessageBox.warning(
                self,
                "G-key already in use",
                f"{data['key']} is already assigned. "
                "to another macro in BearHub.",
            )
            return
            
        macro = Macro(
            id="",
            name=data["name"],
            value=data["value"],
            macro_type=TEXT,
            profile_name="BearHub",
            device_signature="",
            input_id=input_id,
        )
            
        add_macro(
            macro,
            "src/storage/profile.json",
        )
            
        self.view.load_saved_profiles()
            
        bearhub_index = next(
                (
                index
                for index, profile in enumerate(self.view.profiles)
                if profile.get("id") == "bearhub"
            ),
            -1
        )
            
        if bearhub_index >= 0:
            self.view.profile_selector.setCurrentIndex(
                bearhub_index
            )
            
        self.view.status.setText(
            f"Saved {macro.name}."
        )