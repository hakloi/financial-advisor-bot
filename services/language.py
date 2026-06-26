import json

# Function: Set a language using locale .json
# Input: lang (str) - The selected language
# Output: Returns a dictionary with the selected language
def load_language(lang):
    file = (
        "locales/ru.json"
        if lang == "Русский"
        else "locales/en.json"
    )

    with open(file, encoding="utf-8") as f:
        return json.load(f)