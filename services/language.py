import json

# Set a language using locale .json
def load_language(lang):
    file = (
        "locales/ru.json"
        if lang == "Русский"
        else "locales/en.json"
    )

    with open(file, encoding="utf-8") as f:
        return json.load(f)