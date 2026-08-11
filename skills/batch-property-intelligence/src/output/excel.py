"""
Branded Excel output.

Produces a multi-sheet workbook with ELP styling, conditional formatting,
frozen header rows, and auto-filter on every column.

Sheets:
  1. Summary — top-line stats and top 20 scorers
  2. All Properties — every row with all enrichment columns
  3. High Priority — HIGH Seller or HIGH Rental, sorted by Combined Score desc
  4. Portfolios — pivot of owners with 2+ properties
  5. Rentals — properties classified as rentals (Owner Type = Rented)
  6. Filtered Out — government, reserves, non-saleable (transparency)
"""

from pathlib import Path
import pandas as pd
import xlsxwriter


# Standard ELP brand
ELITE_BLACK = "#0A0A0A"
WARM_WHITE = "#F7F4EE"
SOFT_CHARCOAL = "#2A2A2A"
MUTED_GOLD = "#B8965A"
LIGHT_GOLD = "#E8DCC4"

# Output columns and order (used across All Properties + High Priority)
OUTPUT_COLUMNS = [
    "Combined Lead Score",
    "Seller Lead",
    "Rental Lead",
    "Recommended Action",
    "Full Address",
    "Property Type",
    "Bed",
    "Bath",
    "Car",
    "Land Size (m²)",
    "Year Built",
    "Owner 1 Name",
    "Owner Classification",
    "Owner Type",
    "Joint Owner",
    "Owner 2 Name",
    "Owner SC Property Count",
    "Owner SC Rental Count",
    "Owner SC Properties",
    "Owner SC Rentals",
    "Portfolio Investor",
    "Sale Date",
    "Sale Price",
    "Years Since Last Sale",
    "Sale Count",
    "Land Use",
    "Development Zone",
    "Parcel Details",
    "Open in RPData",
]


def write_excel(
    df: pd.DataFrame,
    output_path: Path,
    region_label: str,
    run_timestamp: str,
) -> None:
    """Write the full multi-sheet workbook."""
    workbook = xlsxwriter.Workbook(str(output_path))

    # Define formats
    fmt_title = workbook.add_format({
        "bold": True,
        "font_name": "Arial",
        "font_size": 16,
        "font_color": ELITE_BLACK,
    })
    fmt_subtitle = workbook.add_format({
        "font_name": "Arial",
        "font_size": 10,
        "font_color": SOFT_CHARCOAL,
        "italic": True,
    })
    fmt_header = workbook.add_format({
        "bold": True,
        "font_name": "Arial",
        "font_size": 10,
        "font_color": "#FFFFFF",
        "bg_color": ELITE_BLACK,
        "border": 1,
        "border_color": MUTED_GOLD,
        "align": "left",
        "valign": "vcenter",
        "text_wrap": True,
    })
    fmt_body = workbook.add_format({
        "font_name": "Arial",
        "font_size": 10,
        "valign": "top",
    })
    fmt_high = workbook.add_format({
        "font_name": "Arial",
        "font_size": 10,
        "bg_color": LIGHT_GOLD,
        "bold": True,
        "valign": "top",
    })
    fmt_medium = workbook.add_format({
        "font_name": "Arial",
        "font_size": 10,
        "bg_color": WARM_WHITE,
        "valign": "top",
    })
    fmt_section = workbook.add_format({
        "bold": True,
        "font_name": "Arial",
        "font_size": 12,
        "font_color": MUTED_GOLD,
        "bottom": 2,
        "bottom_color": MUTED_GOLD,
    })

    # === Sheet 1 — Summary ===
    write_summary(workbook, df, fmt_title, fmt_subtitle, fmt_section, fmt_body, fmt_header, fmt_high, region_label, run_timestamp)

    # === Sheet 2 — All Properties ===
    all_df = df.copy()
    write_data_sheet(workbook, "All Properties", all_df, OUTPUT_COLUMNS, fmt_header, fmt_body, fmt_high, fmt_medium)

    # === Sheet 3 — High Priority ===
    high_df = df[
        (df["Seller Lead"] == "HIGH") | (df["Rental Lead"] == "HIGH")
    ].sort_values("Combined Lead Score", ascending=False)
    write_data_sheet(workbook, "High Priority", high_df, OUTPUT_COLUMNS, fmt_header, fmt_body, fmt_high, fmt_medium)

    # === Sheet 4 — Portfolios ===
    portfolios = build_portfolios_pivot(df)
    write_data_sheet(workbook, "Portfolios", portfolios, list(portfolios.columns), fmt_header, fmt_body, fmt_high, fmt_medium)

    # === Sheet 5 — Rentals ===
    rentals_df = df[df["Owner Type"] == "Rented"].sort_values("Combined Lead Score", ascending=False)
    write_data_sheet(workbook, "Rentals", rentals_df, OUTPUT_COLUMNS, fmt_header, fmt_body, fmt_high, fmt_medium)

    # === Sheet 6 — Filtered Out ===
    filtered_df = df[df["Non-Saleable"]]
    filtered_cols = ["Full Address", "Property Type", "Owner 1 Name", "Land Use", "Open in RPData"]
    write_data_sheet(workbook, "Filtered Out", filtered_df, filtered_cols, fmt_header, fmt_body, fmt_high, fmt_medium)

    workbook.close()


def write_summary(workbook, df, fmt_title, fmt_subtitle, fmt_section, fmt_body, fmt_header, fmt_high, region_label, run_timestamp):
    """Write the Summary sheet."""
    ws = workbook.add_worksheet("Summary")
    ws.set_column("A:A", 32)
    ws.set_column("B:B", 50)

    ws.write("A1", "Batch Property Intelligence", fmt_title)
    ws.write("A2", f"Region: {region_label} · Run: {run_timestamp} · Elite Lifestyle Properties", fmt_subtitle)
    ws.write("A3", "")

    # === Top-line counts ===
    ws.write("A5", "TOTALS", fmt_section)
    saleable = df[~df["Non-Saleable"]]
    ws.write_row("A6", ["Total properties", len(df)], fmt_body)
    ws.write_row("A7", ["Saleable properties", len(saleable)], fmt_body)
    ws.write_row("A8", ["Non-saleable (filtered)", len(df) - len(saleable)], fmt_body)

    ws.write("A10", "LEAD GRADE DISTRIBUTION", fmt_section)
    seller_dist = saleable["Seller Lead"].value_counts()
    rental_dist = saleable["Rental Lead"].value_counts()
    ws.write_row("A11", ["Seller Lead: HIGH", int(seller_dist.get("HIGH", 0))], fmt_body)
    ws.write_row("A12", ["Seller Lead: MEDIUM", int(seller_dist.get("MEDIUM", 0))], fmt_body)
    ws.write_row("A13", ["Seller Lead: LOW", int(seller_dist.get("LOW", 0))], fmt_body)
    ws.write_row("A14", ["Seller Lead: NO", int(seller_dist.get("NO", 0))], fmt_body)
    ws.write_row("A15", ["Rental Lead: HIGH", int(rental_dist.get("HIGH", 0))], fmt_body)
    ws.write_row("A16", ["Rental Lead: MEDIUM", int(rental_dist.get("MEDIUM", 0))], fmt_body)
    ws.write_row("A17", ["Rental Lead: LOW", int(rental_dist.get("LOW", 0))], fmt_body)
    ws.write_row("A18", ["Rental Lead: NO", int(rental_dist.get("NO", 0))], fmt_body)

    ws.write("A20", "PORTFOLIOS", fmt_section)
    owners_2plus = saleable[saleable["Owner SC Property Count"] >= 2]["Owner 1 Name"].nunique()
    owners_3plus = saleable[saleable["Owner SC Property Count"] >= 3]["Owner 1 Name"].nunique()
    owners_4plus = saleable[saleable["Owner SC Property Count"] >= 4]["Owner 1 Name"].nunique()
    ws.write_row("A21", ["Owners with 2+ properties", int(owners_2plus)], fmt_body)
    ws.write_row("A22", ["Owners with 3+ properties", int(owners_3plus)], fmt_body)
    ws.write_row("A23", ["Owners with 4+ properties (portfolio investors)", int(owners_4plus)], fmt_body)

    ws.write("A25", "RENTAL MARKET", fmt_section)
    rentals = saleable[saleable["Owner Type"] == "Rented"]
    ws.write_row("A26", ["Total confirmed rentals", len(rentals)], fmt_body)
    ws.write_row("A27", ["Unique landlords", int(rentals["Owner 1 Name"].nunique())], fmt_body)
    ws.write_row("A28", ["Multi-property landlords (2+ rentals)", int(rentals[rentals["Owner SC Rental Count"] >= 2]["Owner 1 Name"].nunique())], fmt_body)

    ws.write("A30", "TOP 20 SCORERS", fmt_section)
    top_20 = df.sort_values("Combined Lead Score", ascending=False).head(20)
    top_cols = ["Combined Lead Score", "Seller Lead", "Rental Lead", "Full Address", "Owner 1 Name", "Recommended Action"]
    for i, col in enumerate(top_cols):
        ws.write(31, i, col, fmt_header)
    for row_idx, (_, row) in enumerate(top_20.iterrows(), start=32):
        fmt = fmt_high if row["Combined Lead Score"] >= 8 else fmt_body
        for col_idx, col in enumerate(top_cols):
            val = row[col]
            if pd.isna(val):
                val = ""
            ws.write(row_idx, col_idx, val, fmt)
    ws.set_column("C:C", 14)
    ws.set_column("D:D", 14)
    ws.set_column("E:E", 35)
    ws.set_column("F:F", 32)
    ws.set_column("G:G", 60)
    ws.freeze_panes(32, 0)


def write_data_sheet(workbook, sheet_name, df, columns, fmt_header, fmt_body, fmt_high, fmt_medium):
    """Write a generic data sheet with headers, body rows, freeze panes, auto-filter."""
    ws = workbook.add_worksheet(sheet_name)
    if df.empty:
        ws.write(0, 0, f"No rows for {sheet_name}", fmt_body)
        return

    # Filter columns to only those present in df
    columns = [c for c in columns if c in df.columns]

    # Header row
    for col_idx, col in enumerate(columns):
        ws.write(0, col_idx, col, fmt_header)

    # Body rows
    for row_idx, (_, row) in enumerate(df.iterrows(), start=1):
        fmt = fmt_body
        if "Combined Lead Score" in df.columns:
            score = row["Combined Lead Score"]
            if score >= 8:
                fmt = fmt_high
            elif score >= 5:
                fmt = fmt_medium
        for col_idx, col in enumerate(columns):
            val = row[col]
            if pd.isna(val):
                val = ""
            elif isinstance(val, bool):
                val = "Y" if val else "N"
            ws.write(row_idx, col_idx, val, fmt)

    # Column widths (approximate sensible defaults)
    col_widths = {
        "Full Address": 40,
        "Owner 1 Name": 30,
        "Owner 2 Name": 25,
        "Owner SC Properties": 50,
        "Owner SC Rentals": 50,
        "Recommended Action": 60,
        "Open in RPData": 50,
        "Land Use": 30,
        "Development Zone": 30,
        "Parcel Details": 18,
    }
    for col_idx, col in enumerate(columns):
        width = col_widths.get(col, 14)
        ws.set_column(col_idx, col_idx, width)

    # Freeze header row + auto-filter
    ws.freeze_panes(1, 0)
    ws.autofilter(0, 0, len(df), len(columns) - 1)


def build_portfolios_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Build a pivot of owners with 2+ properties, sorted by count desc."""
    saleable = df[~df["Non-Saleable"]]
    multi = saleable[saleable["Owner SC Property Count"] >= 2]

    if multi.empty:
        return pd.DataFrame(
            columns=["Owner 1 Name", "Owner Classification", "Property Count", "Rental Count", "SC Properties", "SC Rentals", "Lead Profile"]
        )

    portfolios = (
        multi.drop_duplicates(subset=["Owner 1 Name"])
        .sort_values("Owner SC Property Count", ascending=False)
        [["Owner 1 Name", "Owner Classification", "Owner SC Property Count", "Owner SC Rental Count", "Owner SC Properties", "Owner SC Rentals"]]
        .rename(columns={
            "Owner SC Property Count": "Property Count",
            "Owner SC Rental Count": "Rental Count",
            "Owner SC Properties": "SC Properties",
            "Owner SC Rentals": "SC Rentals",
        })
    )

    # Add a Lead Profile column
    def profile(row):
        if row["Property Count"] >= 4 and row["Rental Count"] >= 2:
            return "Portfolio investor with rentals — top priority"
        if row["Property Count"] >= 4:
            return "Portfolio investor — high priority"
        if row["Rental Count"] >= 2:
            return "Multi-property landlord — PM target"
        if row["Property Count"] >= 3:
            return "Active portfolio holder"
        if row["Rental Count"] >= 1:
            return "Investor with at least one rental"
        return "Multi-property owner-occupier"

    portfolios["Lead Profile"] = portfolios.apply(profile, axis=1)
    return portfolios.reset_index(drop=True)
