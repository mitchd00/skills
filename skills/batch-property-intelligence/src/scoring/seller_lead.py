"""
Seller Lead scoring.

Applies the V1 scoring matrix from the scope document. Returns
HIGH / MEDIUM / LOW / NO for each property.
"""

import pandas as pd


def score_seller_lead(row: pd.Series, long_held_years: float, recent_purchase_years: float) -> str:
    """Score a single property row for Seller Lead potential."""
    # Non-saleable filter
    if row.get("Non-Saleable", False):
        return "NO"

    # Unknown owner
    if not row.get("Has Sale Record", False) or row["Owner 1 Name"] in ("-", "UNKNOWN", ""):
        return "NO"

    count = row.get("Owner SC Property Count", 0)
    classification = row.get("Owner Classification", "Unknown")
    years_held = row.get("Years Since Last Sale", 0)
    owner_type = row.get("Owner Type", "-")

    # 4+ properties = portfolio investor
    if count >= 4:
        return "HIGH"
    # 3 properties
    if count == 3:
        return "HIGH"
    # 2 properties
    if count == 2:
        return "MEDIUM"

    # Single property
    if count == 1:
        # Entity-owned single property → often a holding structure
        if classification == "Entity":
            return "MEDIUM"
        # Individual long-held + absentee (proxied by Rented status when owner not at address)
        if classification == "Individual":
            if years_held >= long_held_years and owner_type == "Rented":
                return "MEDIUM"
            if years_held >= long_held_years:
                return "LOW"
            if years_held < recent_purchase_years:
                return "NO"
            return "LOW"

    return "NO"


def add_seller_lead(df: pd.DataFrame, long_held_years: float, recent_purchase_years: float) -> pd.DataFrame:
    """Append the Seller Lead column to the dataframe."""
    df = df.copy()
    df["Seller Lead"] = df.apply(
        lambda r: score_seller_lead(r, long_held_years, recent_purchase_years), axis=1
    )

    # Add a flag for portfolio investors (4+ properties)
    df["Portfolio Investor"] = df["Owner SC Property Count"] >= 4

    return df
