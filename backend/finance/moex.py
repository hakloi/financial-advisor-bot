import requests 

MOEX_ISS_URL = "https://iss.moex.com/iss/engines/stock/markets/shares/securities.json"

# Get data about shares from MOEX ISS API
def shares_get(params: dict | None = None) -> list[dict]:
    response = requests.get(MOEX_ISS_URL, params=params, timeout=15)
    response.raise_for_status()
    raw = response.json()

    securities = raw.get("securities", {})
    columns = securities.get("columns", [])
    rows = securities.get("data", [])

    return [dict(zip(columns, row)) for row in rows]


# Get data about shares from MOEX ISS API filtered by TQBR board
def get_tqbr_shares(params: dict | None = None) -> list[dict]:
    shares = shares_get(params)
    return [s for s in shares if s["BOARDID"] == "TQBR"]


# Select only the fields required by the application
def prepare_shares(shares: list[dict]) -> list[dict]:
    fields = [
        "SECID",
        "ISIN",
        "SHORTNAME",
        "SECNAME",
        "BOARDID",
        "CURRENCYID",
        "LOTSIZE",
        "FACEVALUE",
        "ISSUESIZE",
        "LISTLEVEL",
        "SECTORID",
    ]

    return [{field: share.get(field) for field in fields} for share in shares]

