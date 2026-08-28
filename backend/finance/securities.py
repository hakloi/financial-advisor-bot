from database.connection import get_connection


# Create the securities table if it does not exist
def init_securities_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS securities (
                    id SERIAL PRIMARY KEY,
                    secid VARCHAR(20) UNIQUE NOT NULL,
                    isin VARCHAR(20),
                    shortname VARCHAR(100),
                    secname VARCHAR(255),
                    board_id VARCHAR(20),
                    currency VARCHAR(10),
                    lot_size INTEGER,
                    face_value NUMERIC,
                    issue_size BIGINT,
                    list_level INTEGER,
                    sector_id VARCHAR(50),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)


# Save or update securities in the database
def save_securities(securities: list[dict]):
    with get_connection() as conn:
        with conn.cursor() as cur:

            for security in securities:
                cur.execute("""
                    INSERT INTO securities (
                        secid,
                        isin,
                        shortname,
                        secname,
                        board_id,
                        currency,
                        lot_size,
                        face_value,
                        issue_size,
                        list_level,
                        sector_id,
                        updated_at
                    )
                    VALUES (
                        %(SECID)s,
                        %(ISIN)s,
                        %(SHORTNAME)s,
                        %(SECNAME)s,
                        %(BOARDID)s,
                        %(CURRENCYID)s,
                        %(LOTSIZE)s,
                        %(FACEVALUE)s,
                        %(ISSUESIZE)s,
                        %(LISTLEVEL)s,
                        %(SECTORID)s,
                        NOW()
                    )
                    ON CONFLICT (secid)
                    DO UPDATE SET
                        isin = EXCLUDED.isin,
                        shortname = EXCLUDED.shortname,
                        secname = EXCLUDED.secname,
                        board_id = EXCLUDED.board_id,
                        currency = EXCLUDED.currency,
                        lot_size = EXCLUDED.lot_size,
                        face_value = EXCLUDED.face_value,
                        issue_size = EXCLUDED.issue_size,
                        list_level = EXCLUDED.list_level,
                        sector_id = EXCLUDED.sector_id,
                        updated_at = NOW()
                """)