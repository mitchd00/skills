"""
Recompute current owners, portfolio counts, and lead scoring across the
entire DB after each ingest.

This is a full rebuild of `parcel_current_owner` and `owners_canonical`
every time — cheap at this scale and trivially deterministic. The
existing scoring modules (src.scoring.*) are reused; we just rehydrate
their dataframe inputs from SQLite first.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

from src.hub.db import connect, owner_key
from src.scoring.combined import add_combined_score
from src.scoring.current_owner import derive_current_owners
from src.scoring.portfolio import add_portfolio_counts
from src.scoring.rental_lead import add_rental_lead
from src.scoring.seller_lead import add_seller_lead


def _load_sales_dataframe(conn) -> pd.DataFrame:
    """Hydrate a sales-history dataframe from SQLite that looks like the CSV ingest output."""
    rows = conn.execute(
        """SELECT
            s.parcel_key,
            p.street_address    AS "Street Address",
            p.suburb            AS "Suburb",
            p.state             AS "State",
            p.postcode          AS "Postcode",
            p.council_area      AS "Council Area",
            p.property_type     AS "Property Type",
            p.bed               AS "Bed",
            p.bath              AS "Bath",
            p.car               AS "Car",
            p.land_size_m2      AS "Land Size Numeric",
            p.floor_size_m2     AS "Floor Size (m²)",
            p.year_built        AS "Year Built",
            p.land_use          AS "Land Use",
            p.development_zone  AS "Development Zone",
            p.parcel_details    AS "Parcel Details",
            p.full_address      AS "Full Address",
            p.open_in_rpdata    AS "Open in RPData",
            s.sale_date         AS sale_date_iso,
            s.sale_price        AS "Sale Price Numeric",
            s.settlement_date   AS "Settlement Date",
            s.sale_type         AS "Sale Type",
            s.agency            AS "Agency",
            s.agent             AS "Agent",
            s.owner1            AS "Owner 1 Name",
            s.owner2            AS "Owner 2 Name",
            s.owner3            AS "Owner 3 Name",
            s.owner_type        AS "Owner Type"
        FROM sales s
        JOIN parcels p ON p.parcel_key = s.parcel_key
        """
    ).fetchall()

    df = pd.DataFrame([dict(r) for r in rows])
    if df.empty:
        return df

    df["Sale Date Parsed"] = pd.to_datetime(df["sale_date_iso"], errors="coerce")
    df["Sale Date"] = df["Sale Date Parsed"].dt.strftime("%d %b %Y").fillna("")
    df["Sale Price"] = df["Sale Price Numeric"].apply(
        lambda v: f"${int(v):,}" if pd.notna(v) else ""
    )
    df["Land Size (m²)"] = df["Land Size Numeric"].astype("Int64").astype(str).replace("<NA>", "")
    df["Owner 1 Name"] = df["Owner 1 Name"].fillna("-")
    df["Owner 2 Name"] = df["Owner 2 Name"].fillna("-")
    df["Owner 3 Name"] = df["Owner 3 Name"].fillna("-")
    df["Owner Type"] = df["Owner Type"].fillna("-")
    df["Vendor 1 Name"] = "-"
    df["Vendor 2 Name"] = "-"
    df["Vendor 3 Name"] = "-"
    return df


def recompute_all(db_path: Path, config_path: Path) -> dict:
    """
    Rebuild parcel_current_owner + owners_canonical across the whole DB.
    Returns a stats dict mirroring the one-shot pipeline's summary.
    """
    with open(config_path) as f:
        config = yaml.safe_load(f)

    with connect(db_path) as conn:
        df_sales = _load_sales_dataframe(conn)
        if df_sales.empty:
            return {"empty": True}

        df_current = derive_current_owners(df_sales)
        df_enriched = add_portfolio_counts(
            df_current,
            entity_patterns=config["entity_patterns"],
            non_saleable_owner_patterns=config["non_saleable_patterns"],
            non_saleable_land_uses=config["non_saleable_land_uses"],
            sc_postcodes=config["sc_postcodes"],
        )
        df_scored = add_seller_lead(
            df_enriched,
            long_held_years=config["long_held_years"],
            recent_purchase_years=config["recent_purchase_years"],
        )
        df_scored = add_rental_lead(df_scored)
        df_final = add_combined_score(df_scored)

        now = datetime.now().isoformat(timespec="seconds")
        conn.execute("DELETE FROM parcel_current_owner")
        conn.execute("DELETE FROM owners_canonical")

        for _, row in df_final.iterrows():
            conn.execute(
                "INSERT OR REPLACE INTO parcel_current_owner (parcel_key, owner_key, derived_at) VALUES (?, ?, ?)",
                (row["parcel_key"], owner_key(row.get("Owner 1 Name", "")), now),
            )

        owners = (
            df_final.drop_duplicates(subset=["Owner 1 Name"])
            .sort_values("Owner SC Property Count", ascending=False)
        )
        for _, row in owners.iterrows():
            name = row.get("Owner 1 Name", "")
            if not name or name in ("-", "UNKNOWN", "NAN"):
                continue
            conn.execute(
                """INSERT OR REPLACE INTO owners_canonical (
                    owner_key, display_name, is_entity, is_filtered, filter_reason,
                    property_count, rental_count,
                    seller_lead, rental_lead, combined_score,
                    recommended_action, last_recomputed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    owner_key(name),
                    name,
                    1 if row.get("Owner Classification") == "Entity" else 0,
                    1 if row.get("Non-Saleable") else 0,
                    "non-saleable pattern" if row.get("Non-Saleable") else None,
                    int(row.get("Owner SC Property Count", 0) or 0),
                    int(row.get("Owner SC Rental Count", 0) or 0),
                    row.get("Seller Lead"),
                    row.get("Rental Lead"),
                    int(row.get("Combined Lead Score", 0) or 0),
                    row.get("Recommended Action"),
                    now,
                ),
            )

    saleable = df_final[~df_final["Non-Saleable"]]
    return {
        "df_final": df_final,
        "sales_records_loaded": len(df_sales),
        "unique_parcels": len(df_final),
        "saleable_parcels": int(len(saleable)),
        "non_saleable_filtered": int(len(df_final) - len(saleable)),
        "seller_high": int((saleable["Seller Lead"] == "HIGH").sum()),
        "seller_medium": int((saleable["Seller Lead"] == "MEDIUM").sum()),
        "seller_low": int((saleable["Seller Lead"] == "LOW").sum()),
        "seller_no": int((saleable["Seller Lead"] == "NO").sum()),
        "rental_high": int((saleable["Rental Lead"] == "HIGH").sum()),
        "rental_medium": int((saleable["Rental Lead"] == "MEDIUM").sum()),
        "rental_low": int((saleable["Rental Lead"] == "LOW").sum()),
        "rental_no": int((saleable["Rental Lead"] == "NO").sum()),
        "owners_2plus": int(saleable[saleable["Owner SC Property Count"] >= 2]["Owner 1 Name"].nunique()),
        "owners_3plus": int(saleable[saleable["Owner SC Property Count"] >= 3]["Owner 1 Name"].nunique()),
        "owners_4plus": int(saleable[saleable["Owner SC Property Count"] >= 4]["Owner 1 Name"].nunique()),
        "confirmed_rentals": int((saleable["Owner Type"] == "Rented").sum()),
    }
