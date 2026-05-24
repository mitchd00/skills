"""Unit tests for the BPI scoring matrix and entity classifier."""

import pandas as pd
import pytest

from src.scoring.combined import combine, SCORE_MATRIX
from src.scoring.portfolio import classify_entity, is_non_saleable
from src.scoring.rental_lead import score_rental_lead
from src.scoring.seller_lead import score_seller_lead


ENTITY_PATTERNS = [
    "PTY LTD", "LIMITED", " LTD", "TRUST", "SUPER", "SMSF",
    "NOMINEES", "HOLDINGS", "INVESTMENTS", "PROPERTIES",
]

NON_SALEABLE_OWNER_PATTERNS = [
    "RESERVE FOR", "SUNSHINE COAST REGIONAL COUNCIL",
    "STATE OF QUEENSLAND", "DEPARTMENT OF", "CHURCH OF",
]

NON_SALEABLE_LAND_USES = ["Reserves", "Recreational", "Public Buildings"]


# ─── classify_entity ──────────────────────────────────────────────────

@pytest.mark.parametrize("name,expected", [
    ("SMITH PTY LTD", "Entity"),
    ("THE JOHN SMITH FAMILY TRUST", "Entity"),
    ("ACME HOLDINGS LIMITED", "Entity"),
    ("SMITH SMSF", "Entity"),
    ("JOHN SMITH", "Individual"),
    ("JANE DOE & JOHN SMITH", "Individual"),
    ("-", "Unknown"),
    ("NAN", "Unknown"),
])
def test_classify_entity(name, expected):
    assert classify_entity(name, ENTITY_PATTERNS) == expected


# ─── is_non_saleable ──────────────────────────────────────────────────

def test_non_saleable_by_owner():
    assert is_non_saleable("RESERVE FOR PARK", "Vacant", NON_SALEABLE_OWNER_PATTERNS, NON_SALEABLE_LAND_USES)
    assert is_non_saleable("CHURCH OF ENGLAND", "Residential", NON_SALEABLE_OWNER_PATTERNS, NON_SALEABLE_LAND_USES)


def test_non_saleable_by_land_use():
    assert is_non_saleable("JOHN SMITH", "Reserves", NON_SALEABLE_OWNER_PATTERNS, NON_SALEABLE_LAND_USES)
    assert is_non_saleable("JOHN SMITH", "Public Buildings", NON_SALEABLE_OWNER_PATTERNS, NON_SALEABLE_LAND_USES)


def test_saleable_individual():
    assert not is_non_saleable("JOHN SMITH", "Residential", NON_SALEABLE_OWNER_PATTERNS, NON_SALEABLE_LAND_USES)


# ─── score_seller_lead ────────────────────────────────────────────────

def _row(**kwargs):
    base = {
        "Non-Saleable": False,
        "Has Sale Record": True,
        "Owner 1 Name": "JOHN SMITH",
        "Owner SC Property Count": 1,
        "Owner Classification": "Individual",
        "Years Since Last Sale": 8,
        "Owner Type": "Owner Occupied",
    }
    base.update(kwargs)
    return pd.Series(base)


def test_seller_portfolio_investor_high():
    assert score_seller_lead(_row(**{"Owner SC Property Count": 5}), 15, 5) == "HIGH"


def test_seller_three_properties_high():
    assert score_seller_lead(_row(**{"Owner SC Property Count": 3}), 15, 5) == "HIGH"


def test_seller_two_properties_medium():
    assert score_seller_lead(_row(**{"Owner SC Property Count": 2}), 15, 5) == "MEDIUM"


def test_seller_entity_single_medium():
    assert score_seller_lead(_row(**{"Owner Classification": "Entity"}), 15, 5) == "MEDIUM"


def test_seller_long_held_absentee_medium():
    assert score_seller_lead(
        _row(**{"Years Since Last Sale": 20, "Owner Type": "Rented"}), 15, 5
    ) == "MEDIUM"


def test_seller_long_held_owner_occupier_low():
    assert score_seller_lead(_row(**{"Years Since Last Sale": 20}), 15, 5) == "LOW"


def test_seller_recent_purchase_no():
    assert score_seller_lead(_row(**{"Years Since Last Sale": 2}), 15, 5) == "NO"


def test_seller_non_saleable_no():
    assert score_seller_lead(_row(**{"Non-Saleable": True}), 15, 5) == "NO"


# ─── score_rental_lead ────────────────────────────────────────────────

def test_rental_multi_property_landlord_high():
    assert score_rental_lead(_row(**{"Owner Type": "Rented", "Owner SC Rental Count": 3})) == "HIGH"


def test_rental_single_landlord_medium():
    assert score_rental_lead(_row(**{"Owner Type": "Rented", "Owner SC Rental Count": 1})) == "MEDIUM"


def test_rental_owner_occupied_no():
    assert score_rental_lead(_row(**{"Owner Type": "Owner Occupied"})) == "NO"


def test_rental_non_saleable_no():
    assert score_rental_lead(_row(**{"Non-Saleable": True, "Owner Type": "Rented"})) == "NO"


# ─── combine ──────────────────────────────────────────────────────────

def test_combined_top_score():
    score, action = combine("HIGH", "HIGH")
    assert score == 10
    assert "portfolio investor" in action.lower()


def test_combined_skip():
    score, _ = combine("NO", "NO")
    assert score == 1


def test_combined_matrix_complete():
    grades = ["HIGH", "MEDIUM", "LOW", "NO"]
    for s in grades:
        for r in grades:
            assert (s, r) in SCORE_MATRIX, f"Missing matrix entry for ({s}, {r})"
