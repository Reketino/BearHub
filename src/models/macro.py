from dataclasses import dataclass

@dataclass
class Macro:
    id:str
    name:str
    text:str
    macro_type: str
     
    profile_name: str = ""
    device_signature: str = ""
    input_id: str = ""