"""
Ingest a single RP Data CSV into the Hub SQLite DB.

Reuses src.sources.rpdata_csv.load_csv for header auto-detection, BOM
handling, sale price/date parsing, and owner-name normalisation. Each CSV
row becomes a `sales` row keyed by (parcel_key, sale_date, sale_price,
owner1) — re-ingesting the same CSV is idempotent (duplicate rows are
silently dropped by INSERT OR IGNORE).
"""

from datetime import datetime
from pathlib import Path

import pandas as pd

from src.hub.db import connect, insert_run, parcel_key, update_run_counts
from src.sources.rpdata_csv import load_csv


def _int_or_none(val):
    try:
        if pd.isna(val):
            return None
        return int(float(val))
    except (TypeError, ValueError):
        return None


def _str_or_none(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).strip()
    return s or None


def ingest_csv(csv_path: Path, db_path: Path, region_hint: str | None = None) -> dict:
    """
    Load one CSV and upsert into the DB. Returns a delta summary.
    """
    df = load_csv(csv_path)
    now = datetime.now().isoformat(timespec="seconds")

    with connect(db_path) as conn:
        run_id = insert_run(conn, str(csv_path.name), len(df), region_hint)

        before_parcels = conn.execute("SELECT COUNT(*) FROM parcels").fetchone()[0]
        before_sales = conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]

        for _, row in df.iterrows():
            pk = parcel_key(
                row.get("Street Address", ""),
                row.get("Suburb", ""),
                row.get("State", ""),
                row.get("Postcode", ""),
            )
            if not pk.strip("|"):
                continue

            conn.execute(
                """INSERT INTO parcels (
                    parcel_key, street_address, suburb, state, postcode,
                    council_area, property_type, bed, bath, car,
                    land_size_m2, floor_size_m2, year_built,
                    land_use, development_zone, parcel_details, full_address, open_in_rpdata,
                    first_seen_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(parcel_key) DO UPDATE SET
                    council_area     = excluded.council_area,
                    property_type    = excluded.property_type,
                    bed              = COALESCE(excluded.bed, parcels.bed),
                    bath             = COALESCE(excluded.bath, parcels.bath),
                    car              = COALESCE(excluded.car, parcels.car),
                    land_size_m2     = COALESCE(excluded.land_size_m2, parcels.land_size_m2),
                    floor_size_m2    = COALESCE(excluded.floor_size_m2, parcels.floor_size_m2),
                    year_built       = COALESCE(excluded.year_built, parcels.year_built),
                    land_use         = excluded.land_use,
                    development_zone = excluded.development_zone,
                    parcel_details   = excluded.parcel_details,
                    full_address     = excluded.full_address,
                    open_in_rpdata   = excluded.open_in_rpdata,
                    last_seen_at     = excluded.last_seen_at
                """,
                (
                    pk,
                    _str_or_none(row.get("Street Address")),
                    _str_or_none(row.get("Suburb")),
                    _str_or_none(row.get("State")),
                    _str_or_none(row.get("Postcode")),
                    _str_or_none(row.get("Council Area")),
                    _str_or_none(row.get("Property Type")),
                    _int_or_none(row.get("Bed")),
                    _int_or_none(row.get("Bath")),
                    _int_or_none(row.get("Car")),
                    _int_or_none(row.get("Land Size Numeric")),
                    _int_or_none(row.get("Floor Size (m²)")),
                    _int_or_none(row.get("Year Built")),
                    _str_or_none(row.get("Land Use")),
                    _str_or_none(row.get("Development Zone")),
                    _str_or_none(row.get("Parcel Details")),
                    _str_or_none(row.get("Full Address")),
                    _str_or_none(row.get("Open in RPData")),
                    now,
                    now,
                ),
            )

            sale_date_parsed = row.get("Sale Date Parsed")
            sale_date_str = (
                sale_date_parsed.date().isoformat()
                if pd.notna(sale_date_parsed)
                else None
            )
            sale_price = row.get("Sale Price Numeric")
            sale_price_val = float(sale_price) if pd.notna(sale_price) else None

            conn.execute(
                """INSERT OR IGNORE INTO sales (
                    parcel_key, sale_date, sale_price, settlement_date,
                    sale_type, agency, agent,
                    owner1, owner2, owner3, owner_type,
                    vendor1, vendor2, vendor3,
                    source_csv, source_run_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pk,
                    sale_date_str,
                    sale_price_val,
                    _str_or_none(row.get("Settlement Date")),
                    _str_or_none(row.get("Sale Type")),
                    _str_or_none(row.get("Agency")),
                    _str_or_none(row.get("Agent")),
                    _str_or_none(row.get("Owner 1 Name")),
                    _str_or_none(row.get("Owner 2 Name")),
                    _str_or_none(row.get("Owner 3 Name")),
                    _str_or_none(row.get("Owner Type")),
                    _str_or_none(row.get("Vendor 1 Name")),
                    _str_or_none(row.get("Vendor 2 Name")),
                    _str_or_none(row.get("Vendor 3 Name")),
                    str(csv_path.name),
                    run_id,
                ),
            )

        after_parcels = conn.execute("SELECT COUNT(*) FROM parcels").fetchone()[0]
        after_sales = conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        new_parcels = after_parcels - before_parcels
        new_sales = after_sales - before_sales

        update_run_counts(conn, run_id, new_parcels, new_sales)

    return {
        "run_id": run_id,
        "rows_in_csv": len(df),
        "new_parcels": new_parcels,
        "new_sales": new_sales,
    }
