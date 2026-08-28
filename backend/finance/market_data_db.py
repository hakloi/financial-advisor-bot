from backend.auth.database import get_connection


# Create the market_data table if it does not exist
def init_market_data_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    id SERIAL PRIMARY KEY,

                    secid VARCHAR(20) NOT NULL,
                    board_id VARCHAR(20) NOT NULL,
                    trade_date DATE NOT NULL,

                    open_price NUMERIC,
                    high_price NUMERIC,
                    low_price NUMERIC,
                    close_price NUMERIC,

                    volume NUMERIC,
                    value NUMERIC,
                    num_trades INTEGER,

                    created_at TIMESTAMP DEFAULT NOW(),

                    UNIQUE (secid, board_id, trade_date)
                )
            """)

# Save historical market data to PostgreSQL
def save_market_data(data: list[dict]):
    with get_connection() as conn:
        with conn.cursor() as cur:

            for row in data:
                cur.execute("""
                    INSERT INTO market_data (
                        secid,
                        board_id,
                        trade_date,
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                        volume,
                        value,
                        num_trades
                    )
                    VALUES (
                        %(SECID)s,
                        %(BOARDID)s,
                        %(TRADEDATE)s,
                        %(OPEN)s,
                        %(HIGH)s,
                        %(LOW)s,
                        %(CLOSE)s,
                        %(VOLUME)s,
                        %(VALUE)s,
                        %(NUMTRADES)s
                    )
                    ON CONFLICT (secid, board_id, trade_date)
                    DO NOTHING
                """, row)


def get_latest_market_context(limit: int = 30) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT secid, board_id, trade_date, open_price,
                          high_price, low_price, close_price, volume, value, num_trades
                   FROM market_data
                   WHERE (secid, board_id, trade_date) IN (
                       SELECT secid, board_id, MAX(trade_date)
                       FROM market_data
                       GROUP BY secid, board_id
                   )
                   ORDER BY secid
                   LIMIT %s""",
                (limit,),
            )
            return [
                {
                    "ticker": row[0],
                    "board": row[1],
                    "trade_date": row[2].isoformat() if row[2] else None,
                    "open": row[3],
                    "high": row[4],
                    "low": row[5],
                    "close": row[6],
                    "volume": row[7],
                    "value": row[8],
                    "trades": row[9],
                }
                for row in cur.fetchall()
            ]