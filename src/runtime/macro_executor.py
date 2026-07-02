import keyboard

from models.macro import Macro

class MacroExecutor:
    def execute(self, macro: Macro):
        print(f"Executing macro: {macro.name}")
        keyboard.write(macro.text)