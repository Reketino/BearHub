import json
from datetime import datetime
from pathlib import Path

def save_profile(macros, output_file):
    profile = {
        "id": "ghub-import",
        "name": "Imported from G hub",
        "imported_at": datetime.now().isoformat(),
        "macro_count": len(macros),
        "macros": []
    }
    
    for macro in macros:
        profile["macros"].append({
            "name": macro.name,
            "text": macro.text,
            "input_id": macro.input_id,
            "preset": macro.profile_name,
            "device": macro.device_signature,
        })
        
    profile["macros"].sort(
        key=lambda m: (
            m["input_id"] == "",
            m["input_id"]
        )
    )
    
    path = Path(output_file)
    
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
    else: 
        data = {"profiles": []}
        
    existing_index = next(
        (
            index
            for index, p in enumerate(data["profiles"])
            if p.get("id") == "ghub-import"
        ),
        None,
    )
    
    if existing_index is not None:
        data["profiles"][existing_index] = profile
    else:
        data["profiles"].append(profile)
        
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )
        
def load_profiles(output_file):
    path = Path(output_file)
    
    if not path.exists():
        return []
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["profiles"]