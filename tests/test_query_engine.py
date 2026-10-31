"""
Unit Tests for Query Engine (Level 3)
=====================================
Tests entity extraction, query intent parsing, and execution on sample datasets.
"""

import os
import sys
import pytest
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.query_engine import (
    extract_years,
    extract_category,
    extract_states,
    extract_parameters,
    parse_query,
    execute_query
)


@pytest.fixture
def query_test_data():
    return pd.DataFrame([
        {"year": 2024, "category": "Engineering", "name": "IIT Test", "score": 90.0, "rank": 1.0, "tlr": 92.0, "rpc": 88.0, "go": 85.0, "oi": 75.0, "perception": 95.0, "state": "Tamil Nadu"},
        {"year": 2024, "category": "Engineering", "name": "NIT Test", "score": 75.0, "rank": 15.0, "tlr": 78.0, "rpc": 70.0, "go": 75.0, "oi": 65.0, "perception": 70.0, "state": "Karnataka"}
    ])


def test_entity_extraction():
    # Test year extraction
    assert extract_years("Rankings in 2024 and 2025") == [2024, 2025]
    assert extract_years("Trend from 2017 to 2023") == [2017, 2023]

    # Test category extraction
    assert extract_category("Engineering colleges in Maharashtra") == "Engineering"
    assert extract_category("Best pharmacy institutions") == "Pharmacy"

    # Test state extraction
    assert "Tamil Nadu" in extract_states("Institutions in Tamil Nadu and Karnataka")

    # Test parameter extraction
    assert "rpc" in extract_parameters("Correlation between RPC and overall score")


def test_parse_query_intents():
    p1 = parse_query("Which states have the most Engineering institutions in the top 100 in 2025?")
    assert p1["intent"] == "top_states"
    assert p1["category"] == "Engineering"
    assert p1["primary_year"] == 2025

    p2 = parse_query("What is the correlation between TLR and RPC in 2024?")
    assert p2["intent"] == "two_var_correlation"

    p3 = parse_query("Which institutions moved from 51-100 to top 50 in 2024?")
    assert p3["intent"] == "band_to_top50"


def test_execute_query(query_test_data):
    plan = {
        "intent": "top_states",
        "category": "Engineering",
        "primary_year": 2024,
        "states": [],
        "parameters": [],
        "institution": None
    }
    res = execute_query(plan, query_test_data)
    assert res["intent"] == "top_states"
    assert "Tamil Nadu" in res["summary_text"]
    assert res["figure"] is not None
    assert not res["data"].empty


def test_execute_empty_query():
    empty_df = pd.DataFrame(columns=["year", "category", "name", "score", "rank", "tlr", "rpc", "go", "oi", "perception", "state"])
    plan = {"intent": "score_trend", "category": "NonExistent", "primary_year": 2024}
    res = execute_query(plan, empty_df)
    assert isinstance(res, dict)
    assert "summary_text" in res
