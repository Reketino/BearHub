import sqlite3
import json
            
from models.macro import Macro

DEBUG = True

def import_macros(db_path: str) -> list[Macro]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    blob = cur.execute(
        "SELECT file FROM data LIMIT 1"
        ).fetchone()[0]

    conn.close()
    
    data = json.loads(blob.decode("utf-8"))
    
    macro_bindings = {}
    
    for card in data.get("cards", {}).get("cards", []):
            if card.get("attribute") != "INPUT_PRESET":
                continue
            
            device_signature = card.get(
                "deviceSignature",
                ""
            )
            
            preset_name = card.get (
                "name",
                ""
            )
            
            assignments = (
                card.get("inputPreset", {})
                .get("assignments", {})
            )
            
            for layer in assignments.values():
                for input_assignment in (
                    layer.get("inputAssignments", {})
                        .values()
                ):
                    
                    input_id = input_assignment.get(
                        "inputId"
                    )
                    
                    modifier_assignments = (
                        input_assignment.get(
                            "modifierAssignments",
                            {}
                        )
                    )
                    
                    for modifier in modifier_assignments.values():
                        events = modifier.get(
                            "eventAssignments",
                            {}
                        )
                        
                        for event in events.values():
                            macro_id = event.get(
                                "macroId"
                            )
                            
                            if macro_id:
                                macro_bindings[
                                    macro_id
                                ] = {
                                    "device": device_signature,
                                    "input_id": str(input_id),
                                    "preset": preset_name,
                                }
    if DEBUG:
        print("\n=== MACRO BINDINGS ===")
        
        for macro_id, binding in macro_bindings.items():
            print(
                macro_id,
                binding["input_id"],
                binding["preset"]
            )
                            
    macros = []
        
    for card in data.get("cards", {}).get("cards", []):
        
        if card.get("attribute") != "MACRO_PLAYBACK":
            continue
           
        macro = card.get("macro", {})
        
        if macro.get("type") != "SEQUENCE":
            continue
        
        sequence = macro.get("sequence", {})
    
        simple = sequence.get("simpleSequence", {})
        
        text = ""
        
        for component in simple.get("components", []):
            if "textBlock" in component:
                text += component["textBlock"].get("text", "")
                
        if not text:
            continue
        
        if DEBUG:
            print(
                f"NAME={card.get('name')} | "
                f"TEXT={text} | "
                
            )
            
        binding = macro_bindings.get(
            card.get("id"),
            {}
        )
                
        macros.append(
            Macro(
                id=card.get("id", ""),
                name=card.get("name", "Unnamed"),
                text=text,
                macro_type=macro.get("type", "UNKNOWN"),
                
                profile_name=binding.get(
                    "preset",
                    ""
                ),
                device_signature=binding.get(
                    "device",
                    ""
                ),
                input_id=binding.get(
                    "input_id",
                    ""
                ),
            )
        )

    return macros