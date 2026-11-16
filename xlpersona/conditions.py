CONDITIONS = ("en", "hi", "ne", "hi_rom", "ne_rom", "hi_cm", "ne_cm")
LANG = {c: c.split("_")[0] for c in CONDITIONS}
KIND = {c: (c.split("_")[1] if "_" in c else "native") for c in CONDITIONS}
LANG_NAME = {"en": "English", "hi": "Hindi", "ne": "Nepali"}
