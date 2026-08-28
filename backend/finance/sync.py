import re

from backend.finance.market_data import get_historical_data
from backend.finance.market_data_db import init_market_data_table, save_market_data
from backend.finance.moex import get_tqbr_shares, prepare_shares
from backend.finance.securities import init_securities_table, save_securities


def refresh_market_data_for_query(
    message: str,
    limit: int = 5,
    max_securities: int = 20,
) -> tuple[int, int]:
    """Refresh only securities mentioned in a user's market-data question."""
    init_securities_table()
    init_market_data_table()

    available = prepare_shares(get_tqbr_shares())
    requested_tickers = {
        ticker.upper() for ticker in re.findall(r"\b[A-Za-z]{2,6}\b", message)
    }
    requested_tickers.discard("MOEX")
    message_lower = message.lower()
    selected = [
        security for security in available
        if security["SECID"].upper() in requested_tickers
        or any(
            value and str(value).lower() in message_lower
            for value in (security.get("SHORTNAME"), security.get("SECNAME"))
        )
    ]
    if not selected:
        selected = [
            security for security in available
            if "ETF" not in str(security.get("SHORTNAME", "")).upper()
        ][:max_securities]

    save_securities(selected)
    history_rows = []
    for security in selected:
        history_rows.extend(
            get_historical_data(
                secid=security["SECID"],
                board_id=security["BOARDID"],
                limit=limit,
            )
        )
    save_market_data(history_rows)
    return len(selected), len(history_rows)


def sync_market_data(limit: int = 100) -> tuple[int, int]:
    """Fetch TQBR securities and their history, then upsert them into PostgreSQL."""
    init_securities_table()
    init_market_data_table()

    securities = prepare_shares(get_tqbr_shares())
    save_securities(securities)

    history_rows = []
    for security in securities:
        history_rows.extend(
            get_historical_data(
                secid=security["SECID"],
                board_id=security["BOARDID"],
                limit=limit,
            )
        )

    save_market_data(history_rows)
    return len(securities), len(history_rows)


if __name__ == "__main__":
    securities_count, history_count = sync_market_data()
    print(f"Saved {securities_count} securities and {history_count} market rows")