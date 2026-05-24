"""
Rental Lead scoring.

Uses RP Data's Owner Type field as the primary signal. V1 only — no REA/Domain
fallback yet (deferred to V1.1).
"""

import pandas as pd


def score_rental_lead(row: pd.Series) -> str:
    """Score a single property row for Rental Lead potential."""
    # Non-saleable filter (also applies — we don't want to PM government properties)
    if row.get("Non-Saleable", False):
        return "NO"

    owner_type = row.get("Owner Type", "-")
    rental_count = row.get("Owner SC Rental Count", 0)

    # Confirmed rental + owner has 2+ rentals = multi-property landlord
    if owner_type == "Rented" and rental_count >= 2:
        return "HIGH"

    # Confirmed rental, single rental in portfolio
    if owner_type == "Rented":
        return "MEDIUM"

    # Unknown owner type — could potentially be a rental
    # V1: mark LOW if owner has rentals elsewhere in their portfolio (suggests investor pattern)
    if owner_type in ("-", "", "Unknown") and rental_count >= 1:
        return "LOW"

    # Owner-occupied confirmed
    if owner_type == "Owner Occupied":
        return "NO"

    return "NO"


def add_rental_lead(df: pd.DataFrame) -> pd.DataFrame:
    """Append the Rental Lead column."""
    df = df.copy()
    df["Rental Lead"] = df.apply(score_rental_lead, axis=1)
    return df
