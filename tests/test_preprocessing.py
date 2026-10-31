"""
Unit Tests for Preprocessing Pipeline
======================================
Tests:
- Cleaning institution names.
- State name standardization.
- Rank value parsing (single ranks and bands).
- Duplicate detection and removal.
- Score and parameter numeric conversions.
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.preprocessing import (
    clean_institution_name,
    standardize_state,
    standardize_category,
    parse_rank_value,
    preprocess_nirf_dataframe
)


def test_clean_institution_name():
    # Should strip HTML leftovers like "More Details", "Close |", extra spaces
    raw1 = "Indian Institute of Technology MadrasMore DetailsClose |"
    assert clean_institution_name(raw1) == "Indian Institute of Technology Madras"

    raw2 = "  Miranda House   \n\n  "
    assert clean_institution_name(raw2) == "Miranda House"

    raw3 = "IIT BombayTLR (100)"
    assert clean_institution_name(raw3) == "IIT Bombay"


def test_standardize_state():
    # Test normalization of common typos and casing
    assert standardize_state("tamilnadu") == "Tamil Nadu"
    assert standardize_state("TAMIL NADU") == "Tamil Nadu"
    assert standardize_state("new delhi") == "Delhi"
    assert standardize_state("pondicherry") == "Puducherry"
    assert standardize_state("karnataka") == "Karnataka"


def test_standardize_category():
    assert standardize_category("overall") == "Overall"
    assert standardize_category("engineering") == "Engineering"
    assert standardize_category("statepublicuniversity") == "State Public University"


def test_parse_rank_value():
    # Normal integer ranks
    assert parse_rank_value("1") == 1.0
    assert parse_rank_value(5) == 5.0

    # Rank bands should parse to midpoint
    assert parse_rank_value("101-150") == 125.5
    assert parse_rank_value("151-200") == 175.5

    # Invalid rank
    assert np.isnan(parse_rank_value("invalid"))


def test_preprocess_synthetic_dataframe():
    # Small synthetic dataset for isolated test
    synthetic_data = pd.DataFrame([
        {
            "year": 2024,
            "category": "engineering",
            "institute_id": "INST-01",
            "name": "Test University A More Details",
            "city": "Bengaluru",
            "state": "karnataka",
            "score": "85.5",
            "rank": "1",
            "tlr": "90.0",
            "rpc": "80.0",
            "go": "85.0",
            "oi": "70.0",
            "perception": "95.0"
        },
        # Duplicate record that should be removed
        {
            "year": 2024,
            "category": "engineering",
            "institute_id": "INST-01",
            "name": "Test University A More Details",
            "city": "Bengaluru",
            "state": "karnataka",
            "score": "85.5",
            "rank": "1",
            "tlr": "90.0",
            "rpc": "80.0",
            "go": "85.0",
            "oi": "70.0",
            "perception": "95.0"
        },
        # Record with out-of-bound score (should be NaN)
        {
            "year": 2024,
            "category": "engineering",
            "institute_id": "INST-02",
            "name": "Test University B",
            "city": "Chennai",
            "state": "tamilnadu",
            "score": "150.0",
            "rank": "2",
            "tlr": "70.0",
            "rpc": "60.0",
            "go": "65.0",
            "oi": "55.0",
            "perception": "50.0"
        }
    ])

    cleaned = preprocess_nirf_dataframe(synthetic_data)

    # 1. Deduplication check: 3 rows -> 2 unique rows
    assert len(cleaned) == 2

    # 2. Name cleaned
    assert cleaned.iloc[0]["name"] == "Test University A"

    # 3. State standardized
    assert cleaned.iloc[0]["state"] == "Karnataka"
    assert cleaned.iloc[1]["state"] == "Tamil Nadu"

    # 4. Out-of-bounds score converted to NaN
    assert np.isnan(cleaned.iloc[1]["score"])
