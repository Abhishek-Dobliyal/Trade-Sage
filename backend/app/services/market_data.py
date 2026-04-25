import logging

import yfinance as yf

log = logging.getLogger(__name__)


def get_bulk_prices(symbols: list[str]) -> dict[str, dict]:
    """Fetch current prices for multiple NSE symbols in batch."""
    results = {}
    for symbol in symbols:
        price = get_stock_price(symbol)
        if price:
            results[symbol] = price
    return results


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
    df = None
    try:
        df = ticker.history(period=period, interval=interval)
    except Exception as e:
        log.warning("yfinance error for %s (%s/%s): %s", symbol, period, interval, e)
        return []
    if df is None or (hasattr(df, 'empty') and df.empty):
        log.warning("No history data returned for %s (period=%s)", symbol, period)
        return []
    try:
        df = df.reset_index()
    except Exception:
        return []
    try:
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
    except Exception:
        log.exception("Failed to parse history data for %s", symbol)
        return []


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
