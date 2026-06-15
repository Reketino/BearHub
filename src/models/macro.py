from dataclasses import dataclass

@dataclass
class Macro:
    id:str
    name:str
    text:str
    macro_type: str = "TEXT"