from database.connection import get_connection


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
                """)