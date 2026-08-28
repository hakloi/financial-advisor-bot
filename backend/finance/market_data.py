import requests


MOEX_HISTORY_URL = (
    "https://iss.moex.com/iss/history/engines/"
    "stock/markets/shares/securities/{secid}.json"
)


# Get historical market data for a specific security
def get_historical_data(
    secid: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 100,
    board_id: str = "TQBR"
) -> list[dict]:

    url = MOEX_HISTORY_URL.format(secid=secid)

    params = {
        "start": 0,
        "limit": limit,
        board_id: board_id
    }

    if start_date:
        params["from"] = start_date

    if end_date:
        params["till"] = end_date

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    raw = response.json()

    history = raw.get("history", {})

    columns = history.get("columns", [])
    rows = history.get("data", [])

    return [
        dict(zip(columns, row))
        for row in rows
    ]