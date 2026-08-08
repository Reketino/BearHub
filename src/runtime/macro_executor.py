import keyboard

from models.macro import Macro

class MacroExecutor:
    def execute(self, macro: Macro):
        print(
            f"Executing macro: "
            f"name={macro.name!r}, "
            f"value={macro.value!r}"
        )
        keyboard.write(macro.value)
        