import time
import keyboard

from models.macro import Macro

class MacroExecutor:
    def execute(self, macro: Macro):
        print(f"Executing macro: {macro.name}")
        time.sleep(2)
        keyboard.write(macro.text)