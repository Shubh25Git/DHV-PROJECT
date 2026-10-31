"""
Unit Tests for Analysis Functions
=================================
Tests statistical and ranking calculations on controlled synthetic datasets.
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

import src.analysis as analysis


@pytest.fixture
def sample_nirf_data():
    """Fixture providing a controlled synthetic dataset across 2 years."""
    return pd.DataFrame([
        # 2023 records
        {"year": 2023, "category": "Overall", "name": "Inst Alpha", "score": 88.0, "rank": 1.0, "tlr": 90.0, "rpc": 85.0, "go": 80.0, "oi": 70.0, "perception": 90.0, "state": "Tamil Nadu"},
        {"year": 2023, "category": "Overall", "name": "Inst Beta", "score": 80.0, "rank": 15.0, "tlr": 75.0, "rpc": 80.0, "go": 75.0, "oi": 65.0, "perception": 70.0, "state": "Karnataka"},
        {"year": 2023, "category": "Overall", "name": "Inst Gamma", "score": 60.0, "rank": 60.0, "tlr": 60.0, "rpc": 55.0, "go": 60.0, "oi": 50.0, "perception": 40.0, "state": "Delhi"},
        {"year": 2023, "category": "Overall", "name": "Inst Delta", "score": 50.0, "rank": 90.0, "tlr": 50.0, "rpc": 45.0, "go": 50.0, "oi": 40.0, "perception": 30.0, "state": "Tamil Nadu"},
        
        # 2024 records
        {"year": 2024, "category": "Overall", "name": "Inst Alpha", "score": 89.0, "rank": 1.0, "tlr": 92.0, "rpc": 86.0, "go": 82.0, "oi": 72.0, "perception": 92.0, "state": "Tamil Nadu"},
        {"year": 2024, "category": "Overall", "name": "Inst Beta", "score": 84.0, "rank": 8.0, "tlr": 80.0, "rpc": 85.0, "go": 78.0, "oi": 68.0, "perception": 75.0, "state": "Karnataka"},  # Moved 15 -> 8 (+7 improve, entered top 10)
        {"year": 2024, "category": "Overall", "name": "Inst Gamma", "score": 68.0, "rank": 40.0, "tlr": 70.0, "rpc": 65.0, "go": 68.0, "oi": 55.0, "perception": 50.0, "state": "Delhi"},  # Moved 60 -> 40 (51-100 to top 50)
        {"year": 2024, "category": "Overall", "name": "Inst Delta", "score": 45.0, "rank": 98.0, "tlr": 45.0, "rpc": 40.0, "go": 45.0, "oi": 35.0, "perception": 25.0, "state": "Tamil Nadu"}  # Declined 90 -> 98 (-8 decline)
    ])


def test_get_institution_rank_trend(sample_nirf_data):
    trend = analysis.get_institution_rank_trend(sample_nirf_data, "Inst Alpha", category="Overall")
    assert len(trend) == 2
    assert list(trend["rank"]) == [1.0, 1.0]
    assert list(trend["year"]) == [2023, 2024]


def test_get_biggest_rank_improvements(sample_nirf_data):
    imp = analysis.get_biggest_rank_improvements(sample_nirf_data, category="Overall", start_year=2023, end_year=2024)
    assert not imp.empty
    # Inst Gamma moved 60 -> 40 (+20 improvement)
    assert imp.iloc[0]["name"] == "Inst Gamma"
    assert imp.iloc[0]["rank_improvement"] == 20.0


def test_get_biggest_rank_declines(sample_nirf_data):
    dec = analysis.get_biggest_rank_declines(sample_nirf_data, category="Overall", start_year=2023, end_year=2024)
    assert not dec.empty
    # Inst Delta moved 90 -> 98 (+8 decline)
    assert dec.iloc[0]["name"] == "Inst Delta"
    assert dec.iloc[0]["rank_decline"] == 8.0


def test_get_states_top_institutions(sample_nirf_data):
    states_df = analysis.get_states_top_institutions(sample_nirf_data, year=2024, category="Overall", top_n=100)
    assert not states_df.empty
    # Tamil Nadu has 2 institutions in top 100 in 2024 (Alpha and Delta)
    tn_row = states_df[states_df["state"] == "Tamil Nadu"]
    assert tn_row.iloc[0]["institution_count"] == 2


def test_get_score_summary_stats(sample_nirf_data):
    stats = analysis.get_score_summary_stats(sample_nirf_data, year=2024, category="Overall")
    assert stats["count"] == 4
    assert stats["max"] == 89.0
    assert stats["min"] == 45.0


def test_get_rpc_vs_score_correlation(sample_nirf_data):
    r, data = analysis.get_rpc_vs_score_correlation(sample_nirf_data, year=2024, category="Overall")
    # Strong positive correlation expected between rpc and score
    assert r > 0.90
    assert len(data) == 4


def test_get_band_to_top50_transitions(sample_nirf_data):
    transitions = analysis.get_band_to_top50_transitions(sample_nirf_data, category="Overall", year1=2023, year2=2024)
    # Inst Gamma was rank 60 in 2023 and rank 40 in 2024
    assert len(transitions) == 1
    assert transitions.iloc[0]["name"] == "Inst Gamma"


def test_get_top10_entries_and_exits(sample_nirf_data):
    top10_mobility = analysis.get_top10_entries_and_exits(sample_nirf_data, category="Overall", year1=2023, year2=2024)
    # Inst Beta entered top 10 (was 15, became 8)
    assert "Inst Beta" in top10_mobility["entries"]
    # Inst Alpha stayed in top 10
    assert "Inst Alpha" in top10_mobility["retained"]


def test_get_mobility_summary(sample_nirf_data):
    mob = analysis.get_mobility_summary(sample_nirf_data, category="Overall", year1=2023, year2=2024)
    # 2 moved up (Beta 15->8, Gamma 60->40)
    # 1 moved down (Delta 90->98)
    # 1 retained (Alpha 1->1)
    assert mob["moved_up"] == 2
    assert mob["moved_down"] == 1
    assert mob["retained_position"] == 1
    assert mob["total_compared"] == 4
