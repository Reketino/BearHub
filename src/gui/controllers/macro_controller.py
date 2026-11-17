
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QMessageBox,
    QDialog,
    QFileDialog,
)

from constants.g_keys import G_KEY_MAP, G_KEY_TO_INPUT_ID
from constants.macro_types import TEXT

from gui.macro_dialog import MacroDialog

from models.macro import Macro

from importers.ghub_importer import import_macros

from storage.profile_storage import (
    add_macro,
    update_macro,
    delete_macro,
    save_profile,
)


PROFILE_PATH = "src/storage/profile.json"


class MacroController:
    def __init__(self, window):
        self.view = window

    # -------- TRIGGER HELPERS -------- #

    @staticmethod
    def get_macro_trigger(macro):
        if macro.trigger_type == "g_key":
            return macro.trigger_value or G_KEY_MAP.get(
                macro.input_id,
                "Unbound",
            )

        return macro.trigger_value or "Unbound"

    @staticmethod
    def get_trigger_label(trigger_type, trigger_value):
        if trigger_type == "g_key":
            return f"G-key: {trigger_value}"

        return f"Keyboard: {trigger_value}"

    def is_trigger_available(
        self,
        profile_id,
        trigger_type,
        trigger_value,
        ignore_index=None,
    ):
        profile = next(
            (
                profile
                for profile in self.view.profiles
                if profile.get("id") == profile_id
            ),
            None,
        )

        if profile is None:
            return True

        for index, macro_data in enumerate(
            profile.get("macros", [])
        ):
            if index == ignore_index:
                continue

            existing_type = macro_data.get(
                "trigger_type",
                "g_key",
            )

            existing_value = macro_data.get(
                "trigger_value",
                "",
            )

            if not existing_value and existing_type == "g_key":
                existing_value = G_KEY_MAP.get(
                    macro_data.get("input_id", ""),
                    "",
                )

            if (
                existing_type == trigger_type
                and existing_value == trigger_value
            ):
                return False

        return True

    @staticmethod
    def get_input_id(trigger_type, trigger_value):
        if trigger_type != "g_key":
            return ""

        return G_KEY_TO_INPUT_ID.get(
            trigger_value,
            "",
        )

    # -------- DISPLAY MACROS -------- #

    def display_macros(self, macros):
        self.view.macro_list.clear()

        for macro in macros:
            trigger_label = self.get_trigger_label(
                macro.trigger_type,
                self.get_macro_trigger(macro),
            )

            self.view.macro_list.addItem(
                f"{macro.name} [{trigger_label}]"
            )

    # -------- SHOW MACRO -------- #

    def show_macro(self, row):
        if row < 0 or row >= len(self.view.macros):
            self.view.edit_macro_button.setEnabled(False)
            self.view.delete_macro_button.setEnabled(False)
            return

        self.view.edit_macro_button.setEnabled(True)
        self.view.delete_macro_button.setEnabled(True)

        macro = self.view.macros[row]

        trigger_label = self.get_trigger_label(
            macro.trigger_type,
            self.get_macro_trigger(macro),
        )

        self.view.details.setPlainText(
            f"Name: {macro.name}\n\n"
            f"Value:\n{macro.value}\n\n"
            f"Trigger: {trigger_label}\n"
            f"Suppress trigger: {macro.suppress_trigger}\n"
            f"Preset: {macro.profile_name}\n"
            f"Device: {macro.device_signature}"
        )

        self.view.status.setText(
            f"Selected {macro.name}"
        )

    # -------- EXECUTE SELECTED MACRO -------- #

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
            lambda: self.execute_macro(macro),
        )

    # -------- EXECUTE MACRO -------- #

    def execute_macro(self, macro):
        self.view.engine.execute_macro(macro)

        self.view.status.setText(
            f"Executed {macro.name}"
        )

    # -------- OPEN MACRO DIALOG -------- #

    def open_macro_dialog(self):
        dialog = MacroDialog(self.view)

        result = dialog.exec()

        if result != QDialog.DialogCode.Accepted:
            return

        data = dialog.get_data()

        target_profile_id = "bearhub"

        if not self.is_trigger_available(
            target_profile_id,
            data["trigger_type"],
            data["trigger_value"],
        ):
            QMessageBox.warning(
                self.view,
                "Trigger already in use",
                f"{data['trigger_value']} is already assigned "
                "to another macro in BearHub.",
            )
            return

        input_id = self.get_input_id(
            data["trigger_type"],
            data["trigger_value"],
        )

        macro = Macro(
            id="",
            name=data["name"],
            value=data["value"],
            macro_type=TEXT,
            profile_name="BearHub",
            device_signature="",
            input_id=input_id,
            trigger_type=data["trigger_type"],
            trigger_value=data["trigger_value"],
            suppress_trigger=data["suppress_trigger"],
        )

        add_macro(macro, PROFILE_PATH)

        self.view.load_saved_profiles()

        bearhub_index = next(
            (
                index
                for index, profile in enumerate(self.view.profiles)
                if profile.get("id") == target_profile_id
            ),
            -1,
        )

        if bearhub_index >= 0:
            self.view.profile_selector.setCurrentIndex(
                bearhub_index
            )

        self.view.status.setText(
            f"Saved {macro.name}."
        )

    # -------- EDIT SELECTED MACRO -------- #

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

        if not self.is_trigger_available(
            self.view.current_profile_id,
            data["trigger_type"],
            data["trigger_value"],
            ignore_index=row,
        ):
            QMessageBox.warning(
                self.view,
                "Trigger already in use",
                f"{data['trigger_value']} is already assigned "
                "to another macro in this profile.",
            )
            return

        input_id = self.get_input_id(
            data["trigger_type"],
            data["trigger_value"],
        )

        updated_macro = Macro(
            id=macro.id,
            name=data["name"],
            value=data["value"],
            macro_type=macro.macro_type,
            profile_name=macro.profile_name,
            device_signature=macro.device_signature,
            input_id=input_id,
            trigger_type=data["trigger_type"],
            trigger_value=data["trigger_value"],
            suppress_trigger=data["suppress_trigger"],
        )

        success = update_macro(
            self.view.current_profile_id,
            row,
            updated_macro,
            PROFILE_PATH,
        )

        if not success:
            self.view.status.setText(
                "Could not update the macro."
            )
            return

        self.view.reload_current_profile()

        if row < self.view.macro_list.count():
            self.view.macro_list.setCurrentRow(row)

        self.view.status.setText(
            f"Updated {updated_macro.name}"
        )

    # -------- DELETE SELECTED MACRO -------- #

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
            PROFILE_PATH,
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

            self.view.macro_list.setCurrentRow(new_row)

        self.view.status.setText(
            f"Deleted {macro.name}."
        )

    # -------- IMPORT GHUB -------- #

    def import_ghub(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Choose settings.db",
            "",
            "Database (*.db)",
        )

        if not file_path:
            return

        macros = import_macros(file_path)

        save_profile(
            macros,
            PROFILE_PATH,
        )

        self.view.load_saved_profiles()

        self.view.status.setText(
            f"Imported {len(macros)} macros."
        )
