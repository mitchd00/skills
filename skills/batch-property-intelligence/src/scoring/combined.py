"""
Combined Lead Score and Recommended Action.

Applies the V1 matrix from the scope document. Combines Seller Lead and
Rental Lead grades into a single score (1-10) and a recommended action.
"""

import pandas as pd


# Score matrix from scope document — keyed by (Seller Lead, Rental Lead)
SCORE_MATRIX = {
    ("HIGH", "HIGH"): (10, "Seller + PM combined pitch — portfolio investor with rentals. Approach with portfolio review framing."),
    ("HIGH", "MEDIUM"): (9, "Seller approach + PM upsell"),
    ("HIGH", "LOW"): (8, "Seller approach — multi-property owner, possible rental in portfolio"),
    ("HIGH", "NO"): (8, "Seller approach — multi-property owner, mostly owner-occupied"),
    ("MEDIUM", "HIGH"): (7, "PM pitch first, seller conversation second"),
    ("MEDIUM", "MEDIUM"): (6, "PM pitch, mention sales side"),
    ("MEDIUM", "LOW"): (5, "Long nurture — DNA Plan #1, possible PM"),
    ("MEDIUM", "NO"): (5, "Long nurture — DNA Plan #1"),
    ("LOW", "HIGH"): (5, "PM pitch only"),
    ("LOW", "MEDIUM"): (4, "PM pitch only"),
    ("LOW", "LOW"): (3, "Long nurture"),
    ("LOW", "NO"): (3, "Long nurture"),
    ("NO", "HIGH"): (4, "PM pitch only — non-saleable but rental opportunity"),
    ("NO", "MEDIUM"): (3, "PM pitch only"),
    ("NO", "LOW"): (2, "Cache for future"),
    ("NO", "NO"): (1, "Skip"),
}


def combine(seller: str, rental: str) -> tuple[int, str]:
    """Return (score, action) for a Seller Lead + Rental Lead grade pair."""
    return SCORE_MATRIX.get((seller, rental), (1, "Skip"))


def add_combined_score(df: pd.DataFrame) -> pd.DataFrame:
    """Append Combined Lead Score and Recommended Action columns."""
    df = df.copy()
    combined = df.apply(
        lambda r: combine(r["Seller Lead"], r["Rental Lead"]), axis=1
    )
    df["Combined Lead Score"] = combined.apply(lambda t: t[0])
    df["Recommended Action"] = combined.apply(lambda t: t[1])
    return df
