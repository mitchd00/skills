"""
RP Data CSV ingest and normalisation.

Handles BOM-encoded UTF-8 CSVs from RP Data exports. Normalises column names,
parses dates, and prepares the dataframe for downstream processing.
"""

from pathlib import Path
import pandas as pd


# Standard RP Data export columns (from inspected May 2026 Currimundi sample)
EXPECTED_COLUMNS = {
    "Street Address",
    "Suburb",
    "State",
    "Postcode",
    "Council Area",
    "Property Type",
    "Bed",
    "Bath",
    "Car",
    "Land Size (m²)",
    "Floor Size (m²)",
    "Year Built",
    "Sale Price",
    "Sale Date",
    "Settlement Date",
    "Sale Type",
    "Agency",
    "Agent",
    "Land Use",
    "Development Zone",
    "Parcel Details",
    "Owner 1 Name",
    "Owner 2 Name",
    "Owner 3 Name",
    "Owner Type",
    "Vendor 1 Name",
    "Vendor 2 Name",
    "Vendor 3 Name",
    "Open in RPData",
}


def _detect_header_row(path: Path) -> int:
    """
    Detect which row contains the actual column headers.

    Some RP Data exports prefix the file with a 'Search String' metadata
    line + blank line before the real headers (typically row 3, index 2).
    Others start with the headers directly (row 1, index 0).

    Returns the 0-indexed row number where the column headers live.
    """
    with open(path, encoding="utf-8-sig") as f:
        for idx, line in enumerate(f):
            if idx > 10:
                # Defensive — if we haven't found a header row in the first
                # 10 lines, fall back to row 0 and let pandas error out
                # informatively rather than hanging
                break
            if "Street Address" in line and "Owner 1 Name" in line:
                return idx
    return 0


def load_csv(path: Path) -> pd.DataFrame:
    """
    Load a single RP Data CSV export. Handles BOM and optional search-metadata
    preamble. Validates columns.

    Returns dataframe with normalised types:
      - 'Sale Date Parsed' as datetime
      - 'Sale Price Numeric' as float (NaN if missing or "Not Disclosed")
      - 'Land Size Numeric' as float (square metres)
      - Owner names uppercased and whitespace-normalised
    """
    header_row = _detect_header_row(path)
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str, header=header_row)

    # Validate
    missing = EXPECTED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"CSV missing expected columns: {missing}. "
            f"Got: {sorted(df.columns)}"
        )

    # Parse sale date (format: "09 Nov 2000")
    df["Sale Date Parsed"] = pd.to_datetime(
        df["Sale Date"], format="%d %b %Y", errors="coerce"
    )

    # Parse sale price ("$16,117,944" → 16117944.0). Handles "Not Disclosed", "-", "" as NaN.
    df["Sale Price Numeric"] = pd.to_numeric(
        df["Sale Price"]
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False),
        errors="coerce",
    )

    # Parse land size ("35,730" → 35730.0). Handles non-numeric as NaN.
    df["Land Size Numeric"] = pd.to_numeric(
        df["Land Size (m²)"].str.replace(",", "", regex=False),
        errors="coerce",
    )

    # Normalise owner names (uppercase, strip, collapse whitespace)
    for col in ("Owner 1 Name", "Owner 2 Name", "Owner 3 Name"):
        df[col] = (
            df[col]
            .fillna("-")
            .astype(str)
            .str.strip()
            .str.upper()
            .str.replace(r"\s+", " ", regex=True)
        )

    # Normalise street address (strip trailing whitespace seen in sample data)
    df["Street Address"] = df["Street Address"].astype(str).str.strip()

    # Build a full address column for downstream use
    df["Full Address"] = (
        df["Street Address"]
        + ", "
        + df["Suburb"].astype(str).str.title()
        + " "
        + df["State"].astype(str)
        + " "
        + df["Postcode"].astype(str)
    )

    return df


def load_csvs(paths: list[Path]) -> pd.DataFrame:
    """Load and concatenate multiple RP Data CSV exports (for cross-suburb portfolio counting)."""
    frames = [load_csv(p) for p in paths]
    return pd.concat(frames, ignore_index=True)
