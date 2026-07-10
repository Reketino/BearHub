from models.macro import Macro
from runtime.macro_executor import MacroExecutor
from runtime.macro_listener import MacroListener
from constants.g_keys import G_KEY_TO_INPUT_ID

class MacroEngine:
    def __init__(self):
        self.profile: list[Macro] = []
        self.running = False
        
        self.executor = MacroExecutor()
        self.listener = MacroListener()
        self.listener.set_callback(
            self.on_key_pressed
        )
       
    def load_profile(self, macros: list[Macro]):
        self.profile = macros
        
        print(
            f"Loaded {len(macros)} macros."
        )
        
    def execute_macro(self, macro):
        self.executor.execute(macro)
        
    def on_key_pressed(self,key):
        print(f"Pressed {key}")
        
        input_id = G_KEY_TO_INPUT_ID.get(key)
        if not input_id:
            return
        for macro in self.profile:
            if macro.input_id == input_id:
                print(f"Executing {macro.name}")
                self.execute_macro(macro)
                return
        
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.listener.start()
        
        print("Macro engine started.")
        
    def stop(self):
        if not self.running:
            return
        
        self.running = False
        self.listener.stop()
        
        print("Macro engine stopped.")