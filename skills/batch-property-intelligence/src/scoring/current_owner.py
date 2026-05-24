"""
Current owner derivation.

RP Data CSV is historical sales. Each row is a sale event. Current owner =
owner from the most recent sale per parcel.
"""

import pandas as pd


def derive_current_owners(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reduce a sales-history dataframe to one row per parcel, keeping the most
    recent sale per parcel as the source of current ownership.

    Returns a dataframe with one row per parcel and the current-owner fields
    populated from the latest sale.
    """
    # Sort by parcel then by sale date desc
    df_sorted = df.sort_values(
        ["Parcel Details", "Sale Date Parsed"],
        ascending=[True, False],
        na_position="last",
    )

    # Keep the first row per parcel (which is the most recent sale)
    current = df_sorted.drop_duplicates(subset=["Parcel Details"], keep="first").copy()

    # Add a flag for parcels with no recorded sale date (treat as unknown ownership)
    current["Has Sale Record"] = current["Sale Date Parsed"].notna()

    # Years since latest sale
    today = pd.Timestamp.today().normalize()
    current["Years Since Last Sale"] = (
        (today - current["Sale Date Parsed"]).dt.days / 365.25
    ).round(1)

    # Count of sales recorded per parcel
    sale_counts = df.groupby("Parcel Details").size().rename("Sale Count")
    current = current.merge(sale_counts, left_on="Parcel Details", right_index=True)

    return current.reset_index(drop=True)
