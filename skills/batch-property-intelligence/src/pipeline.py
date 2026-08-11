"""
Pipeline orchestrator.

Wires together: source ingest → current owner derivation → portfolio counting
→ scoring → output generation.
"""

from pathlib import Path
import yaml
import pandas as pd

from src.sources.rpdata_csv import load_csvs
from src.scoring.current_owner import derive_current_owners
from src.scoring.portfolio import add_portfolio_counts
from src.scoring.seller_lead import add_seller_lead
from src.scoring.rental_lead import add_rental_lead
from src.scoring.combined import add_combined_score
from src.output.excel import write_excel
from src.output.html_report import write_html_report


def load_config(config_path: Path) -> dict:
    """Load the scoring weights YAML."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def run_pipeline(
    input_paths: list[Path],
    output_dir: Path,
    region_label: str,
    run_timestamp: str,
    config_path: Path,
) -> dict:
    """Run the full V1 pipeline. Returns a summary dict."""
    config = load_config(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load CSVs
    df_sales = load_csvs(input_paths)
    sales_count = len(df_sales)

    # 2. Derive current owners
    df_current = derive_current_owners(df_sales)
    current_count = len(df_current)

    # 3. Add portfolio counts and entity classification
    df_enriched = add_portfolio_counts(
        df_current,
        entity_patterns=config["entity_patterns"],
        non_saleable_owner_patterns=config["non_saleable_patterns"],
        non_saleable_land_uses=config["non_saleable_land_uses"],
        sc_postcodes=config["sc_postcodes"],
    )

    # 4. Score Seller Lead
    df_scored = add_seller_lead(
        df_enriched,
        long_held_years=config["long_held_years"],
        recent_purchase_years=config["recent_purchase_years"],
    )

    # 5. Score Rental Lead
    df_scored = add_rental_lead(df_scored)

    # 6. Combined Score + Recommended Action
    df_final = add_combined_score(df_scored)

    # 7. Write outputs
    safe_label = region_label.replace(" ", "_").replace("/", "_")
    xlsx_name = f"{safe_label}_BatchIntelligence_V1_{run_timestamp}.xlsx"
    html_name = f"{safe_label}_BatchIntelligence_Report_V1_{run_timestamp}.html"
    xlsx_path = output_dir / xlsx_name
    html_path = output_dir / html_name

    write_excel(df_final, xlsx_path, region_label, run_timestamp)
    write_html_report(df_final, html_path, region_label, run_timestamp)

    # Summary stats
    saleable = df_final[~df_final["Non-Saleable"]]
    summary = {
        "sales_records_loaded": sales_count,
        "unique_parcels": current_count,
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
        "xlsx_path": str(xlsx_path),
        "html_path": str(html_path),
    }
    return summary
