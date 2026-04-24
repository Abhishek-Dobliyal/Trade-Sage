import csv
import io
import logging

from app.db.models import Holding

log = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"symbol", "name", "type", "quantity", "avg_price"}
OPTIONAL_COLUMNS = {"sector"}

EXPECTED_SCHEMA = """Expected CSV schema:
  symbol    - Ticker symbol (e.g. RELIANCE, INFY, or MF scheme code)
  name      - Company or scheme name
  type      - STOCK or MF
  quantity  - Number of shares or MF units
  avg_price - Average purchase price or NAV
  sector    - (optional) Sector classification
"""


def parse_portfolio_csv(content: str) -> list[Holding]:
    """Parse a portfolio CSV with the standard TradeSage schema.

    The CSV must contain these columns (case-insensitive, whitespace-tolerant):
      symbol, name, type, quantity, avg_price
    Optional: sector
    """
    reader = csv.DictReader(io.StringIO(content))
    raw_fieldnames = reader.fieldnames or []
    fieldnames = {f.strip().lower() for f in raw_fieldnames}

    if not fieldnames:
        raise ValueError("Empty or invalid CSV file.")

    missing = REQUIRED_COLUMNS - fieldnames
    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing))}.\n{EXPECTED_SCHEMA}"
        )

    holdings = []
    skipped = 0
    for line_num, raw_row in enumerate(reader, start=2):
        row = {k.strip().lower(): v.strip() for k, v in raw_row.items()}
        symbol = row.get("symbol", "").upper()
        if not symbol:
            log.warning("Row %d: skipping entry with empty symbol", line_num)
            skipped += 1
            continue

        asset_type = row.get("type", "").upper()
        if asset_type not in ("STOCK", "MF"):
            log.warning(
                "Row %d: invalid type '%s' for %s, defaulting to STOCK",
                line_num, row.get("type", ""), symbol,
            )
            asset_type = "STOCK"

        try:
            quantity = float(row.get("quantity", 0))
            avg_price = float(row.get("avg_price", 0))
        except ValueError:
            log.warning(
                "Row %d: non-numeric quantity/avg_price for %s, skipping",
                line_num, symbol,
            )
            skipped += 1
            continue

        holdings.append(
            Holding(
                symbol=symbol,
                name=row.get("name", symbol),
                asset_type=asset_type,
                quantity=quantity,
                avg_price=avg_price,
                sector=row.get("sector", ""),
            )
        )

    log.info("Parsed %d holdings from CSV (%d rows skipped)", len(holdings), skipped)
    return holdings
