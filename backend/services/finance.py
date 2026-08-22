import yfinance as yf


def get_stock_info(ticker):

    data = yf.Ticker(ticker)
    hist = data.history(period="1mo")

    return {
        "last_price": float(hist["Close"].iloc[-1]),
        "avg_price": float(hist["Close"].mean()),
        "volatility": float(hist["Close"].std())
    }