"""
SQLite schema and connection helpers for the BPI Intelligence Hub.

The Hub accumulates every CSV ever ingested into a single SQLite DB. Current
ownership, portfolio counts, and lead scoring are recomputed across the full
DB on every ingest — so cross-suburb portfolios and longitudinal owner
changes light up automatically once enough CSVs have been dropped.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS parcels (
  parcel_key       TEXT PRIMARY KEY,
  street_address   TEXT,
  suburb           TEXT,
  state            TEXT,
  postcode         TEXT,
  council_area     TEXT,
  property_type    TEXT,
  bed              INTEGER,
  bath             INTEGER,
  car              INTEGER,
  land_size_m2     INTEGER,
  floor_size_m2    INTEGER,
  year_built       INTEGER,
  land_use         TEXT,
  development_zone TEXT,
  parcel_details   TEXT,
  full_address     TEXT,
  open_in_rpdata   TEXT,
  first_seen_at    TIMESTAMP,
  last_seen_at     TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sales (
  parcel_key       TEXT NOT NULL,
  sale_date        TEXT,
  sale_price       REAL,
  settlement_date  TEXT,
  sale_type        TEXT,
  agency           TEXT,
  agent            TEXT,
  owner1           TEXT,
  owner2           TEXT,
  owner3           TEXT,
  owner_type       TEXT,
  vendor1          TEXT,
  vendor2          TEXT,
  vendor3          TEXT,
  source_csv       TEXT,
  source_run_id    INTEGER,
  PRIMARY KEY (parcel_key, sale_date, sale_price, owner1)
);

CREATE TABLE IF NOT EXISTS runs (
  run_id        INTEGER PRIMARY KEY AUTOINCREMENT,
  ingested_at   TIMESTAMP,
  source_csv    TEXT,
  row_count     INTEGER,
  new_parcels   INTEGER,
  new_sales     INTEGER,
  region_hint   TEXT
);

CREATE TABLE IF NOT EXISTS owners_canonical (
  owner_key            TEXT PRIMARY KEY,
  display_name         TEXT,
  is_entity            INTEGER,
  is_filtered          INTEGER,
  filter_reason        TEXT,
  property_count       INTEGER,
  rental_count         INTEGER,
  seller_lead          TEXT,
  rental_lead          TEXT,
  combined_score       INTEGER,
  recommended_action   TEXT,
  last_recomputed_at   TIMESTAMP
);

CREATE TABLE IF NOT EXISTS parcel_current_owner (
  parcel_key   TEXT PRIMARY KEY,
  owner_key    TEXT,
  derived_at   TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sales_parcel ON sales(parcel_key);
CREATE INDEX IF NOT EXISTS idx_sales_owner ON sales(owner1);
CREATE INDEX IF NOT EXISTS idx_parcels_postcode ON parcels(postcode);
"""


DEFAULT_DB_PATH = Path("data/bpi.sqlite")


def parcel_key(street_address: str, suburb: str, state: str, postcode: str) -> str:
    """Stable key for a parcel across CSV exports."""
    parts = [
        (street_address or "").strip().upper(),
        (suburb or "").strip().upper(),
        (state or "").strip().upper(),
        (postcode or "").strip(),
    ]
    return "|".join(parts)


def owner_key(name: str) -> str:
    """Stable key for an owner across rows."""
    if not name:
        return ""
    return " ".join(name.strip().upper().split())


@contextmanager
def connect(db_path: Path = DEFAULT_DB_PATH):
    """Open a SQLite connection, ensure schema, hand back the connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def insert_run(conn, source_csv: str, row_count: int, region_hint: str | None = None) -> int:
    """Insert a run audit row, return the run_id."""
    cur = conn.execute(
        "INSERT INTO runs (ingested_at, source_csv, row_count, new_parcels, new_sales, region_hint) "
        "VALUES (?, ?, ?, 0, 0, ?)",
        (datetime.now().isoformat(timespec="seconds"), source_csv, row_count, region_hint),
    )
    return cur.lastrowid


def update_run_counts(conn, run_id: int, new_parcels: int, new_sales: int) -> None:
    """Patch the run row with the post-ingest delta counts."""
    conn.execute(
        "UPDATE runs SET new_parcels = ?, new_sales = ? WHERE run_id = ?",
        (new_parcels, new_sales, run_id),
    )


def db_stats(conn) -> dict:
    """Return a quick health snapshot for the launcher status pane."""
    return {
        "parcels": conn.execute("SELECT COUNT(*) FROM parcels").fetchone()[0],
        "sales": conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0],
        "owners": conn.execute("SELECT COUNT(*) FROM owners_canonical").fetchone()[0],
        "runs": conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0],
    }
