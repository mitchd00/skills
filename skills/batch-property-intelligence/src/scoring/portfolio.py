"""
Owner portfolio counting and entity classification.

Counts how many properties each owner holds. Classifies owners as Entity
or Individual. Identifies non-saleable parcels.
"""

import pandas as pd


def classify_entity(owner_name: str, entity_patterns: list[str]) -> str:
    """Return 'Entity' if owner name matches any entity pattern, else 'Individual'."""
    if not owner_name or owner_name in ("-", "NAN"):
        return "Unknown"
    upper = owner_name.upper()
    for pattern in entity_patterns:
        if pattern.upper() in upper:
            return "Entity"
    return "Individual"


def is_non_saleable(
    owner_name: str,
    land_use: str,
    non_saleable_owner_patterns: list[str],
    non_saleable_land_uses: list[str],
) -> bool:
    """Return True if the owner or land use matches a non-saleable pattern."""
    if owner_name and owner_name != "-":
        upper_name = owner_name.upper()
        for pattern in non_saleable_owner_patterns:
            if pattern.upper() in upper_name:
                return True
    if land_use and land_use != "-":
        for pattern in non_saleable_land_uses:
            if pattern.lower() in land_use.lower():
                return True
    return False


def add_portfolio_counts(
    df: pd.DataFrame,
    entity_patterns: list[str],
    non_saleable_owner_patterns: list[str],
    non_saleable_land_uses: list[str],
    sc_postcodes: list[int],
) -> pd.DataFrame:
    """
    Append portfolio-counting columns to a current-owner dataframe.

    Adds:
      - Owner Classification (Entity / Individual / Unknown)
      - Non-Saleable (Y/N)
      - Owner SC Property Count (count of parcels in SC postcodes held by this owner)
      - Owner SC Rental Count (count of those parcels with Owner Type = Rented)
      - Owner SC Properties (semicolon-separated address list)
      - Owner SC Rentals (semicolon-separated address list of rentals)
      - Joint Owner (Y/N — does Owner 2 or Owner 3 have a value)
    """
    df = df.copy()

    # Entity classification
    df["Owner Classification"] = df["Owner 1 Name"].apply(
        lambda x: classify_entity(x, entity_patterns)
    )

    # Non-saleable flag
    df["Non-Saleable"] = df.apply(
        lambda row: is_non_saleable(
            row["Owner 1 Name"],
            row["Land Use"],
            non_saleable_owner_patterns,
            non_saleable_land_uses,
        ),
        axis=1,
    )

    # Convert postcode to int for comparison
    df["Postcode Int"] = pd.to_numeric(df["Postcode"], errors="coerce").fillna(0).astype(int)
    sc_postcode_set = set(sc_postcodes)
    df["In SC"] = df["Postcode Int"].isin(sc_postcode_set)

    # Portfolio counting — only count SC properties, only for saleable parcels, only for known owners
    countable = df[
        df["In SC"]
        & ~df["Non-Saleable"]
        & ~df["Owner 1 Name"].isin(["-", "UNKNOWN", "", "NAN"])
    ].copy()

    portfolio = (
        countable.groupby("Owner 1 Name")
        .agg(
            **{
                "Owner SC Property Count": ("Parcel Details", "nunique"),
                "Owner SC Rental Count": (
                    "Owner Type",
                    lambda s: (s == "Rented").sum(),
                ),
                "Owner SC Properties": (
                    "Full Address",
                    lambda s: "; ".join(sorted(set(s))),
                ),
            }
        )
        .reset_index()
    )

    # Build rental address list separately
    rentals_only = countable[countable["Owner Type"] == "Rented"]
    rental_lists = (
        rentals_only.groupby("Owner 1 Name")["Full Address"]
        .apply(lambda s: "; ".join(sorted(set(s))))
        .rename("Owner SC Rentals")
        .reset_index()
    )

    df = df.merge(portfolio, on="Owner 1 Name", how="left")
    df = df.merge(rental_lists, on="Owner 1 Name", how="left")

    # Fill nulls
    df["Owner SC Property Count"] = df["Owner SC Property Count"].fillna(0).astype(int)
    df["Owner SC Rental Count"] = df["Owner SC Rental Count"].fillna(0).astype(int)
    df["Owner SC Properties"] = df["Owner SC Properties"].fillna("")
    df["Owner SC Rentals"] = df["Owner SC Rentals"].fillna("")

    # Joint owner flag
    df["Joint Owner"] = (
        (df["Owner 2 Name"].fillna("-").str.strip() != "-")
        & (df["Owner 2 Name"].fillna("").str.strip() != "")
    )

    return df
