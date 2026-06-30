from models.macro import Macro
from runtime.macro_executor import MacroExecutor

class MacroEngine:
    def __init__(self):
        self.profile: list[Macro] = []
        self.running = False
        self.executor = MacroExecutor()
       
    def load_profile(self, macros: list[Macro]):
        self.profile = macros
        
        print(
            f"Loaded {len(macros)} macros."
        )
        
    def execute_macro(self, macro):
        self.executor.execute(macro)
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        
        print("Macro engine started.")
        
    def stop(self):
        if not self.running:
            return
        
        self.running = False
        
        print("Macro engine stopped.")