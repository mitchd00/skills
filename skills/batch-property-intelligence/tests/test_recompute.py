"""Cross-CSV ingest: an owner appearing in two suburbs gets property_count = 2 after recompute."""

from pathlib import Path

import pytest

from src.hub.db import connect, owner_key
from src.hub.ingest import ingest_csv
from src.hub.recompute import recompute_all


CSV_HEADER = (
    "Street Address,Suburb,State,Postcode,Council Area,Property Type,"
    "Bed,Bath,Car,Land Size (m²),Floor Size (m²),Year Built,"
    "Sale Price,Sale Date,Settlement Date,Sale Type,Agency,Agent,"
    "Land Use,Development Zone,Parcel Details,"
    "Owner 1 Name,Owner 2 Name,Owner 3 Name,Owner Type,"
    "Vendor 1 Name,Vendor 2 Name,Vendor 3 Name,Open in RPData\n"
)


def _row(address, suburb, postcode, owner1, owner_type="Owner Occupied", price="$900,000", date="01 Jun 2019", parcel="L1/RP1"):
    return (
        f'{address},{suburb},QLD,{postcode},Sunshine Coast,House,'
        f'3,2,2,"600",180,2000,'
        f'"{price}",{date},10 Jun 2019,Normal Sale,Acme,Agent,'
        f'Residential,Low Density,{parcel},'
        f'{owner1},-,-,{owner_type},'
        f'PRIOR,-,-,https://example/p\n'
    )


def _write(path: Path, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("﻿" + CSV_HEADER + "".join(rows), encoding="utf-8")


@pytest.fixture
def project(tmp_path: Path):
    csv_4551 = tmp_path / "inputs" / "currimundi.csv"
    _write(csv_4551, [
        _row("10 Test St", "Currimundi", "4551", "SMITH PORTFOLIO PTY LTD", "Rented", parcel="L1/RP1"),
        _row("11 Other St", "Currimundi", "4551", "JANE LOCAL", "Owner Occupied", parcel="L2/RP1"),
    ])
    csv_4575 = tmp_path / "inputs" / "buddina.csv"
    _write(csv_4575, [
        _row("99 Beach Rd", "Buddina", "4575", "SMITH PORTFOLIO PTY LTD", "Rented", parcel="L9/RP9"),
    ])
    config_path = tmp_path / "config" / "scoring-weights.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        """
sc_postcodes:
  - 4551
  - 4575
long_held_years: 15
recent_purchase_years: 5
entity_patterns:
  - "PTY LTD"
  - "LIMITED"
  - "TRUST"
  - "SMSF"
non_saleable_patterns:
  - "RESERVE FOR"
  - "STATE OF QUEENSLAND"
  - "DEPARTMENT OF"
non_saleable_land_uses:
  - "Reserves"
  - "Recreational"
brand: {}
""".strip(),
        encoding="utf-8",
    )
    db_path = tmp_path / "data" / "bpi.sqlite"
    return csv_4551, csv_4575, db_path, config_path


def test_cross_suburb_portfolio_lights_up(project):
    csv_4551, csv_4575, db_path, config_path = project

    ingest_csv(csv_4551, db_path)
    ingest_csv(csv_4575, db_path)

    summary = recompute_all(db_path, config_path)

    assert not summary.get("empty")
    # Three unique parcels, none filtered out
    assert summary["unique_parcels"] == 3
    assert summary["saleable_parcels"] == 3

    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT property_count, rental_count, seller_lead, rental_lead "
            "FROM owners_canonical WHERE owner_key = ?",
            (owner_key("SMITH PORTFOLIO PTY LTD"),),
        ).fetchone()
        assert row is not None
        assert row["property_count"] == 2
        assert row["rental_count"] == 2
        # 2 properties → MEDIUM seller; 2 rentals owned → HIGH rental lead
        assert row["seller_lead"] == "MEDIUM"
        assert row["rental_lead"] == "HIGH"


def test_recompute_idempotent(project):
    csv_4551, csv_4575, db_path, config_path = project
    ingest_csv(csv_4551, db_path)
    ingest_csv(csv_4575, db_path)
    first = recompute_all(db_path, config_path)
    second = recompute_all(db_path, config_path)
    assert first["saleable_parcels"] == second["saleable_parcels"]
    assert first["seller_high"] == second["seller_high"]
    assert first["rental_high"] == second["rental_high"]
