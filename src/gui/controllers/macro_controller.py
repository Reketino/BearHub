from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QMessageBox,
    QDialog,
    QFileDialog,
)

from constants.g_keys import G_KEY_MAP
from constants.macro_types import TEXT

from gui.macro_dialog import MacroDialog

from models.macro import Macro

from importers.ghub_importer import import_macros

from storage.profile_storage import (
    add_macro,
    update_macro,
    delete_macro,
    is_key_available,
    save_profile,
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
        
        self.view.details.setPlainText(
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
                self.view,
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
        
 #-------- EDIT SELECTED MACRO --------#
        
    def edit_selected_macro(self):
        row = self.view.macro_list.currentRow()
        
        if row < 0 or row >= len(self.view.macros):
            self.view.status.setText(
                "Select a macro to edit."
            )
            return
        
        if self.view.current_profile_id is None:
            self.view.status.setText(
                "No profile selected."
            )
            return
        
        macro = self.view.macros[row]
        
        dialog = MacroDialog(
            self.view,
            macro=macro,
        )
        
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
            "",
        )
        
        if not is_key_available(
            self.view.current_profile_id,
            input_id,
            "src/storage/profile.json",
            ignore_index=row
        ):
            QMessageBox.warning(
                self.view,
                "G-key already in use",
                f"{data['key']} is already assigned "
                "to another macro in this profile."
            )
            return
        
        updated_macro = Macro(
            id=macro.id,
            name=data["name"],
            value=data["value"],
            macro_type=macro.macro_type,
            profile_name=macro.profile_name,
            device_signature=macro.device_signature,
            input_id=input_id,
        )
        
        success = update_macro(
            self.view.current_profile_id,
            row,
            updated_macro,
            "src/storage/profile.json"
        )
        
        if not success:
            self.view.status.setText(
                "Could not update the macro"
            )
            return
        
        self.view.reload_current_profile()
        if row < self.view.macro_list.count():
            self.view.macro_list.setCurrentRow(row)
        
        self.view.status.setText(
            f"Updated {updated_macro.name}"
        )
        
 #-------- DELETE SELECTED MACRO --------#
    
    def delete_selected_macro(self):
        row = self.view.macro_list.currentRow()
        
        if row < 0 or row >= len(self.view.macros):
            return
        
        if self.view.current_profile_id is None:
            self.view.status.setText(
                "No profile selected."
            )
            return
        
        macro = self.view.macros[row]
        
        answer = QMessageBox.question(
            self.view,
            "Delete Macro",
            f"Delete '{macro.name}'?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        
        if answer != QMessageBox.StandardButton.Yes:
            return
        
        success = delete_macro(
            self.view.current_profile_id,
            row,
            "src/storage/profile.json"
        )
        
        if not success:
            self.view.status.setText(
                "Could not delete macro."
            )
            return
        
        self.view.reload_current_profile()
        
        if self.view.macro_list.count() > 0:
            new_row = min(
                row,
                self.view.macro_list.count() - 1,
            )
            
            self.view.macro_list.setCurrentRow(
                new_row
            )
        
        self.view.status.setText(
            f"Deleted {macro.name}."
        )
        
    #-------- IMPORT GHUB --------#
    
    def import_ghub(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
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
        
        self.view.load_saved_profiles()
        self.view.status.setText(
            f"Imported {len(macros)} macros."
        )