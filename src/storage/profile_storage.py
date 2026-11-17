
import json
from datetime import datetime
from pathlib import Path

from constants.g_keys import G_KEY_MAP


def _macro_to_dict(macro) -> dict:
    """Convert a Macro object into the profile JSON format."""
    input_id = macro.input_id or ""

    return {
        "name": macro.name,
        "value": macro.value,
        "macro_type": macro.macro_type,
        "input_id": input_id,
        "preset": macro.profile_name,
        "device": macro.device_signature,
        "trigger_type": macro.trigger_type or "g_key",
        "trigger_value": (
            macro.trigger_value
            or G_KEY_MAP.get(input_id, "")
        ),
        "suppress_trigger": macro.suppress_trigger,
    }


def _read_profile_data(path: Path) -> dict:
    """Read profile data or return an empty profile structure."""
    if not path.exists():
        return {"profiles": []}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_profile_data(path: Path, data: dict) -> None:
    """Write profile data to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def save_profile(macros, output_file):
    profile = {
        "id": "ghub-import",
        "name": "Imported from G hub",
        "imported_at": datetime.now().isoformat(),
        "macro_count": len(macros),
        "macros": [
            _macro_to_dict(macro)
            for macro in macros
        ],
    }

    profile["macros"].sort(
        key=lambda macro: (
            macro["input_id"] == "",
            macro["input_id"],
        )
    )

    path = Path(output_file)
    data = _read_profile_data(path)

    existing_index = next(
        (
            index
            for index, existing_profile in enumerate(data["profiles"])
            if existing_profile.get("id") == "ghub-import"
        ),
        None,
    )

    if existing_index is not None:
        data["profiles"][existing_index] = profile
    else:
        data["profiles"].append(profile)

    _write_profile_data(path, data)


def load_profiles(output_file):
    path = Path(output_file)

    if not path.exists():
        return []

    data = _read_profile_data(path)
    return data.get("profiles", [])


def add_macro(macro, output_file):
    path = Path(output_file)
    data = _read_profile_data(path)

    profile = next(
        (
            profile
            for profile in data["profiles"]
            if profile.get("id") == "bearhub"
        ),
        None,
    )

    if profile is None:
        profile = {
            "id": "bearhub",
            "name": "BearHub",
            "created_at": datetime.now().isoformat(),
            "macro_count": 0,
            "macros": [],
        }

        data["profiles"].append(profile)

    profile["macros"].append(_macro_to_dict(macro))
    profile["macro_count"] = len(profile["macros"])

    _write_profile_data(path, data)


def update_macro(
    profile_id,
    macro_index,
    macro,
    output_file,
):
    path = Path(output_file)

    if not path.exists():
        return False

    data = _read_profile_data(path)

    profile = next(
        (
            profile
            for profile in data["profiles"]
            if profile.get("id") == profile_id
        ),
        None,
    )

    if profile is None:
        return False

    if not 0 <= macro_index < len(profile["macros"]):
        return False

    profile["macros"][macro_index] = _macro_to_dict(macro)
    profile["macro_count"] = len(profile["macros"])

    _write_profile_data(path, data)
    return True


def delete_macro(
    profile_id,
    macro_index,
    output_file,
):
    path = Path(output_file)

    if not path.exists():
        return False

    data = _read_profile_data(path)

    profile = next(
        (
            profile
            for profile in data["profiles"]
            if profile.get("id") == profile_id
        ),
        None,
    )

    if profile is None:
        return False

    if not 0 <= macro_index < len(profile["macros"]):
        return False

    del profile["macros"][macro_index]
    profile["macro_count"] = len(profile["macros"])

    _write_profile_data(path, data)
    return True


def is_key_available(
    profile_id,
    input_id,
    output_file,
    ignore_index=None,
):
    path = Path(output_file)

    if not path.exists():
        return True

    data = _read_profile_data(path)

    profile = next(
        (
            profile
            for profile in data["profiles"]
            if profile.get("id") == profile_id
        ),
        None,
    )

    if profile is None:
        return True

    for index, macro in enumerate(profile["macros"]):
        if index == ignore_index:
            continue

        if macro.get("input_id", "") == input_id:
            return False

    return True
