import json
import os
from pathlib import Path


# Official sources about deposits from five main banks in Russia
BANK_DEPOSITS = {
    "Сбербанк": {
        "url": "https://digital.sber.ru/ru/person/contributions/deposits",
        "description": "Вклады Сбербанка"
    },

    "Газпромбанк": {
        "url": "https://www.gazprombank.ru/personal/increase/deposits/",
        "description": "Вклады Газпромбанка"
    },

    "ВТБ": {
        "url": "https://втб.рф/personal/vklady-i-scheta/",
        "description": "Вклады ВТБ"
    },

    "Альфа Банк": {
        "url": "https://alfabank.sale/make-money/deposits/",
        "description": "Вклады Альфа Банка"
    },

    "Т-Банк": {
        "url": "https://www.tbank.ru/savings/deposit/",
        "description": "Вклады Т-Банка"
    }
}

DEPOSIT_QUERY_PATTERN = (
    "вклад|вклады|вложени|депозит|депозиты|ставк|накопитель|сбережен|"
    "deposit|deposits|saving|savings|interest rate|банк|банки|банка|"
    "ссылк|рекоменд|recommend|bank"
)


def is_deposit_query(message: str) -> bool:
    """Return whether a message is asking about bank deposits."""
    import re

    return re.search(DEPOSIT_QUERY_PATTERN, message, flags=re.IGNORECASE) is not None


def load_deposits() -> list[dict]:
    """Load the latest scraped deposit data when the optional JSON file exists."""
    configured_path = os.getenv("DEPOSITS_DATA_PATH")
    paths = [
        Path(configured_path) if configured_path else None,
        Path(__file__).resolve().parents[2] / "deposits.json",
        Path.cwd() / "deposits.json",
    ]

    for path in paths:
        if path and path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError):
                return []
            return data if isinstance(data, list) else []
    return []


def format_deposits_context(deposits: list[dict]) -> str:
    """Create compact, explicit source data for the LLM context."""
    sources = [
        {"bank": bank, "description": data["description"], "url": data["url"]}
        for bank, data in BANK_DEPOSITS.items()
    ]
    if not deposits:
        return json.dumps(
            {
                "offers": [],
                "official_sources": sources,
                "instruction": "There are no parsed offers. Provide these official links and do not invent deposit names or rates.",
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )

    return json.dumps({"offers": deposits, "official_sources": sources}, ensure_ascii=False, separators=(",", ":"))


# Function to get all banks
def get_all_banks():
    return BANK_DEPOSITS


# Function to get specific bank
def get_bank_deposit_url(bank_name: str):
    bank_name = bank_name.lower().strip()

    for bank, data in BANK_DEPOSITS.items():
        if bank.lower() == bank_name:
            return data["url"]

    return None