from typing import Final

G_KEY_MAP = {
    "399": "G1",
    "400": "G2",
    "401": "G3",
    "402": "G4",
    "403": "G5",
    "404": "G6",
    "405": "G7",
    "406": "G8",
    "407": "G9",
}

G_KEY_TO_INPUT_ID: Final[dict[str, str]] = {
    g_key: input_id
    for input_id, g_key in G_KEY_MAP.items()
}