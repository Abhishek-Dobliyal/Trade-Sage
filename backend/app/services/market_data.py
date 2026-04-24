import logging

import yfinance as yf

log = logging.getLogger(__name__)


def get_stock_price(symbol: str) -> dict | None:
    """Fetch current price info for an NSE/BSE stock."""
    ticker = yf.Ticker(f"{symbol}.NS")
    try:
        info = ticker.fast_info
        return {
            "symbol": symbol,
            "current_price": info.last_price,
            "previous_close": info.previous_close,
            "day_change": round(info.last_price - info.previous_close, 2),
            "day_change_pct": round(
                (info.last_price - info.previous_close) / info.previous_close * 100, 2
            ),
            "market_cap": getattr(info, "market_cap", None),
        }
    except Exception:
        log.exception("Failed to fetch price for %s", symbol)
        return None


def get_stock_history(
    symbol: str, period: str = "6mo", interval: str = "1d"
) -> list[dict]:
    """Fetch historical OHLCV data."""
    ticker = yf.Ticker(f"{symbol}.NS")
    try:
        df = ticker.history(period=period, interval=interval)
    except Exception:
        log.exception("Failed to fetch history for %s", symbol)
        return []
    if df.empty:
        log.warning("No history data returned for %s (period=%s)", symbol, period)
        return []
    df = df.reset_index()
    return [
        {
            "date": row["Date"].isoformat(),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2),
            "volume": int(row["Volume"]),
        }
        for _, row in df.iterrows()
    ]


def get_index_quotes() -> list[dict]:
    """Fetch major Indian market indices."""
    indices = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
        "NIFTY BANK": "^NSEBANK",
    }
    results = []
    for name, ticker_symbol in indices.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.fast_info
            results.append(
                {
                    "name": name,
                    "value": round(info.last_price, 2),
                    "previous_close": round(info.previous_close, 2),
                    "change": round(info.last_price - info.previous_close, 2),
                    "change_pct": round(
                        (info.last_price - info.previous_close)
                        / info.previous_close
                        * 100,
                        2,
                    ),
                }
            )
        except Exception:
            log.exception("Failed to fetch index %s (%s)", name, ticker_symbol)
    return results
