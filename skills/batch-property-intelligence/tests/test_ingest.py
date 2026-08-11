"""End-to-end test: synthetic CSV → DB upsert → idempotent re-ingest."""

from pathlib import Path

import pytest

from src.hub.db import connect
from src.hub.ingest import ingest_csv


CSV_HEADER = (
    "Street Address,Suburb,State,Postcode,Council Area,Property Type,"
    "Bed,Bath,Car,Land Size (m²),Floor Size (m²),Year Built,"
    "Sale Price,Sale Date,Settlement Date,Sale Type,Agency,Agent,"
    "Land Use,Development Zone,Parcel Details,"
    "Owner 1 Name,Owner 2 Name,Owner 3 Name,Owner Type,"
    "Vendor 1 Name,Vendor 2 Name,Vendor 3 Name,Open in RPData\n"
)

CURRIMUNDI_ROW_1 = (
    "10 Test Street,Currimundi,QLD,4551,Sunshine Coast,House,"
    '3,2,2,"600",180,1995,'
    '"$850,000",15 Mar 2018,30 Mar 2018,Normal Sale,Acme Realty,Jane Agent,'
    "Residential,Low Density,L1/RP12345,"
    "SMITH JOHN PETER,SMITH MARY ANN,-,Owner Occupied,"
    "PREVIOUS OWNER,-,-,https://rpdata.example/p1\n"
)

CURRIMUNDI_ROW_2 = (
    "22 Sample Avenue,Currimundi,QLD,4551,Sunshine Coast,House,"
    '4,2,2,"720",210,2005,'
    '"$1,200,000",10 Jan 2020,25 Jan 2020,Normal Sale,Acme Realty,Bob Agent,'
    "Residential,Low Density,L2/RP12345,"
    "BROWN PORTFOLIO PTY LTD,-,-,Rented,"
    "PREVIOUS OWNER,-,-,https://rpdata.example/p2\n"
)


def _write_csv(path: Path, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # BOM + header + rows
    text = "﻿" + CSV_HEADER + "".join(rows)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def synth_csv(tmp_path: Path) -> Path:
    csv = tmp_path / "inputs" / "synth.csv"
    _write_csv(csv, [CURRIMUNDI_ROW_1, CURRIMUNDI_ROW_2])
    return csv


def test_ingest_inserts_parcels_and_sales(synth_csv: Path, tmp_path: Path):
    db = tmp_path / "data" / "bpi.sqlite"
    delta = ingest_csv(synth_csv, db)

    assert delta["rows_in_csv"] == 2
    assert delta["new_parcels"] == 2
    assert delta["new_sales"] == 2

    with connect(db) as conn:
        parcels = conn.execute("SELECT COUNT(*) FROM parcels").fetchone()[0]
        sales = conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        runs = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        assert parcels == 2
        assert sales == 2
        assert runs == 1


def test_re_ingest_is_idempotent(synth_csv: Path, tmp_path: Path):
    db = tmp_path / "data" / "bpi.sqlite"
    first = ingest_csv(synth_csv, db)
    second = ingest_csv(synth_csv, db)

    assert first["new_sales"] == 2
    assert second["new_sales"] == 0
    assert second["new_parcels"] == 0

    with connect(db) as conn:
        sales = conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        runs = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        assert sales == 2          # no duplicates
        assert runs == 2           # but both ingests are audit-logged


def test_ingest_persists_owner_and_owner_type(synth_csv: Path, tmp_path: Path):
    db = tmp_path / "data" / "bpi.sqlite"
    ingest_csv(synth_csv, db)

    with connect(db) as conn:
        row = conn.execute(
            "SELECT owner1, owner_type FROM sales WHERE owner1 LIKE 'BROWN PORTFOLIO%'"
        ).fetchone()
        assert row is not None
        assert row["owner1"] == "BROWN PORTFOLIO PTY LTD"
        assert row["owner_type"] == "Rented"
